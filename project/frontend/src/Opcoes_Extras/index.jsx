import Card_Opcao from "../Card_Opcao";

const Opcoes_Extras = ({ onSelect }) => {

  const opcoes = [
    "Qual o futuro da inteligência artificial na criação de conteúdo?",
    "Por que a Revolução Industrial começou na Inglaterra?",
    "Como a mudança climática afeta a produção de café no mundo?",
    "O que eu deveria saber sobre os impostos no Brasil?",
    "Como funciona o mercado cripto?",
  ];

  return (
    <div>
      <p className="text-white mb-2 mt-6">
        Não sabe por onde começar? Experimente uma destas opções:
      </p>

      <div>
        {opcoes.map((texto, index) => (
          <div 
            key={index}
            className="bg-gradient-to-r from-[rgba(255,208,147)] to-[rgba(235,175,255)] p-0.5 rounded mb-2 w-fit hover:shadow-xl transition transform duration-300 hover:-translate-y-1"
          >
            <button
              className="hover:cursor-pointer bg-[#616161] text-white rounded p-2 text-x opacity-75"
              onClick={() => onSelect(texto)}
            >
              <Card_Opcao pergunta={texto} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Opcoes_Extras;
