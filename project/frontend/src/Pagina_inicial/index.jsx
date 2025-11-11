import { useState } from "react";
import Barra_Pesquisa from "../Barra_Pesquisa";
import Opcoes_Extras from "../Opcoes_Extras";
import Titulo from "../titulo";

const Pagina_inicial = ({ setResultado, setLoading }) => {
  const [pesquisa, setPesquisa] = useState({ topico: "" });

  async function processarPergunta(textoFinal) {
    try {
      const resposta = await fetch("http://127.0.0.1:8000/api/processar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pergunta: textoFinal })
      });

      const dados = await resposta.json();
      setResultado(dados);
    } catch (error) {
      console.error("Error", error);
      setResultado({ error: "Erro ao se comunicar com o servidor" });
    }

    setLoading(false);
  }

  async function handleSubmit(textoManual) {
    const textoFinal = textoManual !== undefined ? textoManual : pesquisa.topico;
    if (!textoFinal.trim()) return;

    // anima fade-out
    const page = document.querySelector("#paginaInicial");
    page.classList.add("animate-fadeOut");

    setTimeout(() => {
      setLoading(true);
      processarPergunta(textoFinal);
    }, 250);
  }

  return (
    <div
      id="paginaInicial"
      className="mt-12 animate-fadeIn opacity-0"
    >
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
