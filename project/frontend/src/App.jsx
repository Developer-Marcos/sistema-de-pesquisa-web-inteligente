import Pagina_inicial from "./Pagina_inicial"
import LimiteFooter from "./LimiteFooter";
import LimiteHeader from "./LimiteHeader";

function App() {

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-t from-[#C1C1C1] to-[#5B5B5B] ">
      <LimiteHeader />
      <main className="flex-grow flex items-center justify-center">
        <Pagina_inicial />
      </main>
      <LimiteFooter />
    </div> 
  )
}

export default App
