import Barra_Pesquisa from "../Barra_Pesquisa";
import Opcoes_Extras from "../Opcoes_Extras";
import Titulo from "../titulo";

const Pagina_inicial = () => {
      return(
            <div>
                  <Titulo />
                  <Barra_Pesquisa />
                  <Opcoes_Extras />
            </div>
            
      );  
}

export default Pagina_inicial