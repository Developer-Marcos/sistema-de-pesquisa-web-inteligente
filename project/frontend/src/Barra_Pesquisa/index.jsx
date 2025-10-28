import iconePesquisa from '../svg/icone-pesquisa.svg?url';

const Barra_Pesquisa = () => {
    return(
      <div>
        <form className='w-120'>
            <div className="shadow-md p-0.5 rounded-full bg-gradient-to-r from-[rgba(255,208,147)] to-[rgba(235,175,255)] w-140">
                <div className="bg-gradient-to-r from-[#FFFFFF] to-[#5B5B5B] rounded-full shadow-md flex items-center"> 
                    <input type="text" placeholder="Insira o tópico de pesquisa" className="flex-grow pl-4 pt-2 pb-2 text-lg bg-transparent focus:outline-none"/>
                    <button type="submit" className="p-2.5 w-12 h-12 flex items-center justify-center rounded-full bg-transparent hover:cursor-pointer hover:opacity-50">
                        <img 
                            src={iconePesquisa} 
                            alt="Ícone de Pesquisa" 
                            className="w-6 h-6" 
                        />
                    </button>
                </div>
            </div>
        </form>
            <div className='m-2 mb-4 text-sm opacity-50'>O sistema buscará informações relevantes e criará um estudo<br/> completo sobre sua questão.</div>
        </div>
    )
}

export default Barra_Pesquisa