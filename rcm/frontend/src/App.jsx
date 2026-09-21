import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Departments from "./pages/Departments";
import Doctors from "./pages/Doctors";
import Patients from "./pages/Patients";
import Diagnoses from "./pages/Diagnoses";
import Payments from "./pages/Payments";
import LabTests from "./pages/LabTests";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-[#F3F5F7]">
        <Sidebar />
        <main className="flex-1 p-6 lg:p-8 max-w-[1400px]">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/departments" element={<Departments />} />
            <Route path="/doctors" element={<Doctors />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/diagnoses" element={<Diagnoses />} />
            <Route path="/payments" element={<Payments />} />
            <Route path="/lab-tests" element={<LabTests />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
