import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";

export default function TelaCarregamento({ setResultado, setLoading }) {
  const [progresso, setProgresso] = useState(0);
  const target = useRef(0);
  const [etapa, setEtapa] = useState("Preparando o sistema...");
  const autoProgressDone = useRef(false);

  const initialTarget = useRef(10 + Math.random() * 5);

  useEffect(() => {
    let ativo = true;
    const eventSource = new EventSource("http://127.0.0.1:8000/stream");

    const animate = () => {
      if (!ativo) return;

      setProgresso(prev => {
        let diff = target.current - prev;
        let incremento = Math.min(diff * 0.05, 0.5);

        if (!autoProgressDone.current && prev >= initialTarget.current) {
          incremento = 0.05;
          target.current = prev + incremento;
        }

        return Math.max(prev, prev + incremento);
      });

      requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);

    const autoProgress = () => {
      if (!ativo) return;

      if (!autoProgressDone.current) {
        if (target.current < initialTarget.current) {
          target.current += 0.1;
          requestAnimationFrame(autoProgress);
        } else {
          autoProgressDone.current = true;
        }
      }
    };
    requestAnimationFrame(autoProgress);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (!ativo) return;

        if (data.percentual !== undefined) {
          target.current = Math.max(target.current, data.percentual);
        }

        if (data.etapa) setEtapa(data.etapa);

        if (data.done) {
          eventSource.close();
          target.current = 100;
          setTimeout(() => {
            if (ativo) {
              setResultado(data.resultado || {});
              setLoading(false);
            }
          }, 500);
        }
      } catch (e) {
        console.error("Erro SSE", e);
      }
    };

    eventSource.onerror = () => {
      if (!ativo) return;
      console.error("Erro SSE");
      setEtapa("Conexão perdida...");
      eventSource.close();
      setLoading(false);
    };

    return () => {
      ativo = false;
      eventSource.close();
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center w-full gap-4 text-white">
      <div className="w-64 h-2 bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: "rgba(255, 255, 255, 0.3)" }} // barra mais transparente
          animate={{ width: `${progresso}%` }}
          transition={{ duration: 0.1 }}
        />
      </div>

      <p className="text-sm opacity-80">{Math.round(progresso)}%</p>
      <p className="text-lg animate-pulse">{etapa}</p>
    </div>
  );
}
