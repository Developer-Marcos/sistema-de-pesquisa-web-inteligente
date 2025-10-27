import Pagina_inicial from "./Pagina_inicial"
import LimiteFooter from "./LimiteFooter";
import LimiteHeader from "./LimiteHeader";

function App() {

  return (
    <div>
      <LimiteHeader />
      <main>
        <Pagina_inicial />
      </main>
      <LimiteFooter />
    </div>
  )
}

export default App
