import { useState } from "react";
import Pagina_inicial from "./Pagina_inicial";
import TelaCarregamento from "./Tela_Carregamento";
import Pagina_final from "./Pagina_final";
import LimiteFooter from "./LimiteFooter";
import LimiteHeader from "./LimiteHeader";

function App() {
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="bg-gradient-to-t from-[#FFD093] to-[#EBAFFF] min-h-screen">
      <div className="flex flex-col min-h-screen bg-black opacity-70">
        <LimiteHeader />

        <main className="flex-grow flex justify-center overflow-y-auto">
          {!resultado && !loading && (
            <Pagina_inicial 
              setResultado={setResultado}
              setLoading={setLoading}
            />
          )}

          {loading && !resultado && <TelaCarregamento />}

          {resultado && !loading && (
            <Pagina_final pesquisa={resultado} setResultado={setResultado} />
          )}
        </main>

        <LimiteFooter />
      </div>
    </div>
  );
}

export default App;
