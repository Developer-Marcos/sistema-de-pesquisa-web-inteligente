import { useState } from "react";
import Barra_Pesquisa from "../Barra_Pesquisa";
import Opcoes_Extras from "../Opcoes_Extras";
import Titulo from "../titulo";

const Pagina_inicial = ({ setResultado, setLoading }) => {
  const [pesquisa, setPesquisa] = useState({ topico: "" });

  async function processarPergunta(textoFinal) {
    try {
      await fetch("http://127.0.0.1:8000/api/processar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pergunta: textoFinal })
      });

    } catch (error) {
      console.error("Erro", error);
      setResultado({ error: "Erro ao se comunicar com o servidor" });
      setLoading(false);
    }
  }

  async function handleSubmit(textoManual) {
    const textoFinal = textoManual !== undefined ? textoManual : pesquisa.topico;
    if (!textoFinal.trim()) return;

    setLoading(true);
    await processarPergunta(textoFinal);
  }

  return (
    <div>
      <Titulo />

      <Barra_Pesquisa 
        pesquisa={pesquisa}
        setPesquisa={setPesquisa}
        onSubmit={handleSubmit}
      />

      <Opcoes_Extras 
        onSelect={(texto) => {
          setPesquisa({ topico: texto });
          handleSubmit(texto);
        }}
      />
    </div>
  );
};

export default Pagina_inicial;
