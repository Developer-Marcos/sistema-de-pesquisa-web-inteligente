import Card_Opcao from "../Card_Opcao"

const Opcoes_Extras = () => {
      return(
            <div>
                  <p>Não sabe por onde começar? Experimente uma destas opções:</p>
                  <div>
                        <Card_Opcao pergunta="Qual o futuro da inteligência artificial na criação de conteúdo?"/>
                        <Card_Opcao pergunta="Por que a Revolução Industrial começou na Inglaterra?"/>
                        <Card_Opcao pergunta="Como a mudança climática afeta a produção de café no mundo?"/>
                        <Card_Opcao pergunta="Como funciona o mercado cripto?"/>
                  </div>
            </div>
      )
}

export default Opcoes_Extras