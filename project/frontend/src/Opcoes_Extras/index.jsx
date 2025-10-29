import Card_Opcao from "../Card_Opcao"

const Opcoes_Extras = () => {
      return(
            <div>
                  <p className="text-white mb-2 mt-6">Não sabe por onde começar? Experimente uma destas opções:</p>
                  <div>
                        <div className="bg-gradient-to-r from-[rgba(255,208,147)] to-[rgba(235,175,255)] p-0.5 rounded mb-2 w-fit hover:shadow-xl transition transform duration-300 hover:-translate-y-1">
                              <button className="hover:cursor-pointer bg-[#616161] text-white rounded p-2 text-x opacity-75"><Card_Opcao pergunta="Qual o futuro da inteligência artificial na criação de conteúdo?"/></button>
                        </div>
                        <div className="bg-gradient-to-r from-[rgba(255,208,147)] to-[rgba(235,175,255)] p-0.5 rounded mb-2 w-fit hover:shadow-xl transition transform duration-300 hover:-translate-y-1">
                              <button className="hover:cursor-pointer bg-[#616161] text-white rounded p-2 text-x opacity-75"><Card_Opcao pergunta="Por que a Revolução Industrial começou na Inglaterra?"/></button>
                        </div>
                        <div className="bg-gradient-to-r from-[rgba(255,208,147)] to-[rgba(235,175,255)] p-0.5 rounded mb-2 w-fit hover:shadow-xl transition transform duration-300 hover:-translate-y-1">
                              <button className="hover:cursor-pointer bg-[#616161] text-white rounded p-2 text-x opacity-75"><Card_Opcao pergunta="Como a mudança climática afeta a produção de café no mundo?"/></button>
                        </div>
                        <div className="bg-gradient-to-r from-[rgba(255,208,147)] to-[rgba(235,175,255)] p-0.5 rounded mb-2 w-fit hover:shadow-xl transition transform duration-300 hover:-translate-y-1">
                              <button className="hover:cursor-pointer bg-[#616161] text-white rounded p-2 text-x opacity-75"><Card_Opcao pergunta="O que eu deveria saber sobre os impostos no Brasil?"/></button>
                        </div> 
                        <div className="bg-gradient-to-r from-[rgba(255,208,147)] to-[rgba(235,175,255)] p-0.5 rounded w-fit hover:shadow-xl transition transform duration-300 hover:-translate-y-1">
                              <button className="hover:cursor-pointer bg-[#616161] text-white rounded p-2 text-x opacity-75"><Card_Opcao pergunta="Como funciona o mercado cripto?"/></button>
                        </div> 
                  </div>
            </div>
      )
}

export default Opcoes_Extras