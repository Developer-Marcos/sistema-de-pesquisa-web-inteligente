import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";

export default function TelaCarregamento({ setResultado, setLoading }) {
  const [progresso, setProgresso] = useState(0);
  const [etapa, setEtapa] = useState("Preparando o sistema...");
  const [frase, setFrase] = useState("");
  const target = useRef(0);
  const autoProgressDone = useRef(false);
  const initialTarget = useRef(10 + Math.random() * 5);
  const eventSourceRef = useRef(null);

  const frasesCarregamento = [
    "Aguarde um momento, por favor.",
    "Estamos processando sua solicitação...",
    "Gerando sua resposta, só mais um instante.",
    "O sistema está trabalhando para você.",
    "Analisando e preparando o resultado.",
    "Aguardando a conclusão do processamento.",
    "Obrigado por sua paciência.",
    "Processamento em andamento...",
    "Sua resposta será exibida em breve."
  ];

  useEffect(() => {
    const fraseAleatoria =
      frasesCarregamento[Math.floor(Math.random() * frasesCarregamento.length)];
    setFrase(fraseAleatoria);

    let ativo = true;
    const eventSource = new EventSource("http://127.0.0.1:8000/stream");
    eventSourceRef.current = eventSource;

    const animate = () => {
      if (!ativo) return;
      setProgresso((prev) => {
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

  const handleVoltar = () => {
    if (eventSourceRef.current) eventSourceRef.current.close();

    fetch("http://127.0.0.1:8000/abort", { method: "POST" }).catch(console.error);

    setLoading(false);
    setResultado(null);
  };

  return (
    <div className="flex flex-col w-full gap-2 text-white">
      <p className="text-2xl">{frase}</p>

      <div className="flex items-center gap-4 w-full">
        <div className="p-[2px] bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)] w-full">
          <div className="h-6 bg-black/65 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)]"
              animate={{ width: `${progresso}%` }}
              transition={{ duration: 0.1 }}
            />
          </div>
        </div>
        <p className="text-xl opacity-80 text-[#EBAFFF]">{Math.round(progresso)}%</p>
      </div>

      <span className="text-sm animate-pulse bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent block">
        {etapa}
      </span>

      <p className="text-white fixed bottom-4 left-4 opacity-60">
        Lembrando: Tópicos mais complexos podem exigir mais tempo de processamento.
      </p>

      <p className="text-white fixed bottom-4 right-4 opacity-60">
        Demorando muito?{" "}
        <button
          className="hover:cursor-pointer hover:opacity-20 underline"
          onClick={handleVoltar}
        >
          Voltar
        </button>
      </p>
    </div>
  );
}
