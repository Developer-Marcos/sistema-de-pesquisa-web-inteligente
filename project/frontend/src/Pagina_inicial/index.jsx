import { useState } from "react";
import Barra_Pesquisa from "../Barra_Pesquisa";
import Opcoes_Extras from "../Opcoes_Extras";
import Titulo from "../titulo";

const Pagina_inicial = () => {

  const [pesquisa, setPesquisa] = useState({ topico: "" });
  const [resultado, setResultado] = useState(null);
  const [carregar, setCarregar] = useState(false);

  async function handleSubmit() {
    if (!pesquisa.topico) {
      alert("Digite algo para pesquisar");
      return;
    }

    setCarregar(true);
    setResultado(null);

    try {
      const resposta = await fetch("http://127.0.0.1:8000/api/processar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pergunta: pesquisa.topico })
    });


      const dados = await resposta.json();
      setResultado(dados);
    } catch (error) {
      console.error("Error", error);
      setResultado({error: "Erro ao se comunicar com o servidor"});
    }

    setCarregar(false);
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
          handleSubmit();
        }}
      />

      {carregar && (
        <p className="text-white mt-4 opacity-80">Gerando sua resposta</p>
      )}

      {resultado && (
        <div className="bg-white text-black p-4 rounded mt-4 w-3/5 mx-auto shadow-lg">
          <h3 className="font-bold mb-2">Resultado</h3>
          <pre className="text-xs whitespace-pre-wrap">
            {JSON.stringify(resultado, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default Pagina_inicial;
