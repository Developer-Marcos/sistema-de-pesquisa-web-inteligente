import iconeLink from '../svg/link_icon.svg?url'

const Pagina_final = ({ pesquisa }) => {
  return (
    <div className="text-white p-6 max-w-5xl mx-auto">
      
      <p className="bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent mb-2">
        Resultado da pesquisa:
      </p>
      <h1 className="text-3xl font-bold mb-4">{pesquisa.titulo_da_analise}</h1>

      <div className="shadow-md p-[1px] mb-4 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)]"></div>

      <p className="mb-6">
        <span className="bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent text-lg">
          Resumo do assunto:
        </span>
        <br /> {pesquisa.resumo_executivo}
      </p>

      <div className="shadow-md p-[1px] mb-4 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)]"></div>

      {pesquisa.campos_dinamicos.map((campo, index) => (
        <div key={index} className="pb-2">
          <h2 className="bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent text-lg">
            ● {campo.nome}:
          </h2>
          <p>{campo.descricao}</p>
          <div className="shadow-md p-[1px] mb-4 mt-8 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)]"></div>
        </div>
      ))}

      <div className="mt-6">
            <h3 className="text-lg font-semibold bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent text-lg">- Fontes Citadas:</h3>
            <p className='my-2'>Veja de onde vieram as informações e descubra mais sobre o tema:</p>
            <div className="space-y-2">
                  {pesquisa.fontes_citadas.map((fonte) => {
                        const url_limpa = fonte
                        .replace(/^https?:\/\//, "")
                        .replace(/^www\./, "")
                        .split("/")[0]
                        .split("?")[0];

                        return (
                        <a key={fonte} href={fonte} target="_blank" rel="noopener noreferrer"
                        className="space-x-2 text-black shadow-md p-2 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)] rounded hover:shadow-xl hover:-translate-y-0.5 transition transform duration-300 hover:cursor-pointer hover:opacity-75 transition flex mr-160">
                              <img src={iconeLink} alt="Ícone de Pesquisa" className="w-6 h-6" />
                              <span>{url_limpa}</span>
                        </a>
                        );
                  })}
            </div>
      </div>

      <div className="shadow-md p-[1px] my-8 bg-gradient-to-r from-[rgba(255,208,147,0.74)] to-[rgba(235,175,255,0.74)]"></div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Especificações:</h3>
        <pre className="bg-black/50 p-4 rounded text-sm overflow-auto">
          {JSON.stringify(pesquisa.especificacoes, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default Pagina_final;
