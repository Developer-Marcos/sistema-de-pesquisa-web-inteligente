import { useState } from "react";
import Barra_Pesquisa from "../Barra_Pesquisa";
import Opcoes_Extras from "../Opcoes_Extras";
import Titulo from "../titulo";

const Pagina_inicial = () => {

  const [pesquisa, setPesquisa] = useState({ topico: "" });

  function handleSubmit() {
    console.log("Buscando por:", pesquisa.topico);
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
    </div>
  );
};

export default Pagina_inicial;
