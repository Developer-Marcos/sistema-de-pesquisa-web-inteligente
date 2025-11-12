import { useState } from "react";
import { motion } from "framer-motion";
import iconeLink from "../svg/link_icon.svg?url";

const Pagina_final = ({ pesquisa, setResultado }) => {
  const [showSpecs, setShowSpecs] = useState(false);

  if (!pesquisa) {
    return (
      <div className="text-white p-6">
        Carregando resultado…
      </div>
    );
  }

  const dados = pesquisa;
  const campos = dados?.campos_dinamicos || [];
  const fontes = dados?.fontes_citadas || [];
  
  return (
    <motion.div
      className="text-white p-6 max-w-5xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      <button
        onClick={() => setResultado(null)}
        className="mb-4 text-sm px-3 py-2 rounded bg-white/10 hover:bg-white/20 transition hover:cursor-pointer"
      >
        Nova pesquisa
      </button>

      <p className="bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent mb-2">
        Resultado da pesquisa:
      </p>

      <h1 className="text-3xl font-bold mb-4">{dados.titulo_da_analise}</h1>

      <div className="shadow-md p-[1px] mb-4 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)]"></div>

      <p className="mb-6">
        <span className="bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent text-lg">
          Resumo do assunto:
        </span>
        <br /> {dados.resumo_executivo}
      </p>

      <div className="shadow-md p-[1px] mb-4 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)]"></div>

      {campos?.map((campo, index) => (
        <div key={index} className="pb-2">
          <h2 className="bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent text-lg">
            ● {campo.nome}:
          </h2>
          <p>{campo.descricao}</p>
          <div className="shadow-md p-[1px] mb-4 mt-8 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)]"></div>
        </div>
      ))}

      <div className="mt-6">
        <h3 className="text-lg font-semibold bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent text-lg">
          - Fontes Citadas:
        </h3>
        <p className="my-2">Veja de onde vieram as informações e descubra mais sobre o tema:</p>
        <div className="space-y-2">
          {fontes?.map((fonte) => {
            const url_limpa = fonte
              .replace(/^https?:\/\//, "")
              .replace(/^www\./, "")
              .split("/")[0]
              .split("?")[0];

            return (
              <a
                key={fonte}
                href={fonte}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center gap-2 text-black shadow-md p-2 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)] rounded hover:shadow-xl hover:-translate-y-0.5 hover:opacity-75 transition"
              >
                <img src={iconeLink} alt="Ícone de Pesquisa" className="w-6 h-6" />
                <span>{url_limpa}</span>
                <span className="text-xs opacity-20 group-hover:opacity-60 transition ml-2 hidden md:inline">
                  {fonte}
                </span>
              </a>
            );
          })}
        </div>
      </div>

      <div className="shadow-md p-[1px] my-8 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)]"></div>

      <div>
  <button
    onClick={() => setShowSpecs(!showSpecs)}
    className="text-lg font-semibold bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent hover:cursor-pointer hover:opacity-75 transition"
  >
    {showSpecs ? "Ocultar Especificações ▲" : "Mostrar Especificações ▼"}
  </button>

  {showSpecs && dados.especificacoes && (
    <ul className="mt-2 text-sm space-y-1 list-disc list-inside p-2 animate-specOpen">
      {Object.entries(dados.especificacoes).map(([chave, valor]) => (
        <li key={chave} className="px-2 py-1">
          <span className="font-semibold bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent">
            {chave}:
          </span>{" "}
          <span className="opacity-90">{String(valor)}</span>
        </li>
      ))}
    </ul>
  )}
</div>

    </motion.div>
  );
};

export default Pagina_final;
