import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Departments from "./pages/Departments";
import Doctors from "./pages/Doctors";
import Patients from "./pages/Patients";
import Diagnoses from "./pages/Diagnoses";
import Payments from "./pages/Payments";
import LabTests from "./pages/LabTests";
import Appointments from "./pages/Appointments";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen min-w-0 flex-col bg-[#F4F7FB] lg:flex-row">
        <Sidebar />
        <main className="min-w-0 max-w-[1400px] flex-1 p-4 sm:p-6 lg:p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/departments" element={<Departments />} />
            <Route path="/doctors" element={<Doctors />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/diagnoses" element={<Diagnoses />} />
            <Route path="/payments" element={<Payments />} />
            <Route path="/lab-tests" element={<LabTests />} />
            <Route path="/appointments" element={<Appointments />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
