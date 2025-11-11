import iconePesquisa from '../svg/icone-pesquisa.svg?url';

const Barra_Pesquisa = ({ pesquisa, setPesquisa, onSubmit }) => {

  function handleChange(e) {
    setPesquisa({ ...pesquisa, [e.target.name]: e.target.value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit();
  }

  return (
    <div className="flex flex-col">
      <form className="w-full max-w-[560px]" onSubmit={handleSubmit}>
        <div className="shadow-md p-0.5 rounded-full bg-gradient-to-r from-[rgba(255,208,147)] to-[rgba(235,175,255)] focus-within:shadow-xl focus-within:-translate-y-1 hover:shadow-xl hover:-translate-y-1 transition transform duration-300">
          <div className="bg-black rounded-full shadow-md flex items-center bg-opacity-70"> 
            
            <input 
              name="topico"
              onChange={handleChange}
              value={pesquisa.topico}
              type="text"
              placeholder="Insira o tópico de pesquisa"
              autoComplete="off"
              aria-label="Campo de pesquisa"
              className="flex-grow pl-4 py-2 text-lg focus:outline-none text-white placeholder-gray-300"
            />

            <button 
              type="submit" 
              className="p-2.5 w-12 h-12 flex items-center justify-center rounded-full bg-transparent hover:cursor-pointer hover:opacity-75 transition"
            >
              <img src={iconePesquisa} alt="Ícone de Pesquisa" className="w-6 h-6" />
            </button>

          </div>
        </div>
      </form>

      <div className="mt-6 mb-4 text-sm bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent text-center">
        O sistema buscará informações relevantes e criará um estudo completo sobre sua questão.
      </div>
    </div>
  );
};

export default Barra_Pesquisa;
