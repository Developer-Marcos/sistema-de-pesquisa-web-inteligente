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
    <div>
      <form className='w-120' onSubmit={handleSubmit}>
        <div className="shadow-md p-0.5 rounded-full bg-gradient-to-r from-[rgba(255,208,147)] to-[rgba(235,175,255)] w-140 focus-within:shadow-xl focus-within:-translate-y-1 hover:shadow-xl hover:-translate-y-1 transition transform duration-300">
          <div className="bg-black rounded-full shadow-md flex items-center opacity-70"> 
            
            <input 
              name="topico"
              onChange={handleChange}
              value={pesquisa.topico}
              type="text"
              placeholder="Insira o tópico de pesquisa"
              autocomplete="off"
              className="flex-grow pl-4 pt-2 pb-2 text-lg focus:outline-none text-white"
            />

            <button type="submit" className="p-2.5 w-12 h-12 flex items-center justify-center rounded-full bg-transparent hover:cursor-pointer hover:opacity-50">
              <img src={iconePesquisa} alt="Ícone de Pesquisa" className="w-6 h-6" />
            </button>

          </div>
        </div>
      </form>

      <div className='m-2 mb-4 text-sm bg-gradient-to-r from-[#FFD093] to-[#EBAFFF] bg-clip-text text-transparent'>
        O sistema buscará informações relevantes e criará um estudo<br/> completo sobre sua questão.
      </div>
      
    </div>
  );
};

export default Barra_Pesquisa;
