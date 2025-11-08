import Pagina_inicial from "./Pagina_inicial"
import LimiteFooter from "./LimiteFooter";
import LimiteHeader from "./LimiteHeader";

function App() {

  return (
    <div className="bg-gradient-to-t from-[#FFD093] to-[#EBAFFF]">
      <div className="flex flex-col min-h-screen bg-black opacity-70">
        <LimiteHeader />
        <main className="flex-grow flex items-center justify-center">
          <Pagina_inicial />
        </main>
        <LimiteFooter />
      </div>
    </div> 
  )
}

export default App
