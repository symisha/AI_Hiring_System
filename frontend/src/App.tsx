import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import About from "./pages/About";
import Contact from "./pages/Contact";
import HRLogin from "./pages/HRLogin";
import HRSignup from "./pages/HRSignup";
import CandidateLogin from "./pages/CandidateLogin";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";
import Apply from "./pages/Apply";
import ProtectedRoutes from "./components/ProtectedRoutes";
import FormPage from "./pages/form";
import JobForm from "./pages/JobForm";
const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/hr-login" element={<HRLogin />} />
          <Route path="/hr-signup" element={<HRSignup />} />
          <Route path="/candidate-login" element={<CandidateLogin />} />
          <Route path="/apply" element={<Apply />} />
          <Route path="/dashboard" element={<ProtectedRoutes><Dashboard /></ProtectedRoutes>} />
          <Route path="/form" element={<FormPage />} />  
          <Route path="/upload-job" element={<JobForm />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
