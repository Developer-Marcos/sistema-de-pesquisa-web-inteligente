import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
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

        <main className="flex-grow flex justify-center items-center">
  <div className="flex flex-col justify-center w-full max-w-5xl px-4 py-8 items-center">
    <AnimatePresence mode="wait">
      {!resultado && !loading && (
        <motion.div
          key="inicio"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.35 }}
        >
          <Pagina_inicial 
            setResultado={setResultado}
            setLoading={setLoading}
          />
        </motion.div>
      )}

      {loading && !resultado && (
        <motion.div
          key="carregando"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
        >
          <TelaCarregamento />
        </motion.div>
      )}

      {resultado && !loading && (
        <motion.div
          key="resultado"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.35 }}
        >
          <Pagina_final pesquisa={resultado} setResultado={setResultado} />
        </motion.div>
      )}
    </AnimatePresence>
  </div>
</main>



        <LimiteFooter />
      </div>
    </div>
  );
}

export default App;
