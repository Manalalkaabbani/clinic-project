import { useState } from "react";
import Modal from "./Modal";

export default function RegistrationModal({ open, onClose, onRegister, initialName = "" }) {
  const [name, setName] = useState(initialName);
  const [error, setError] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmedName = name.trim();

    if (!trimmedName) {
      setError("Please enter your name.");
      return;
    }

    onRegister(trimmedName);
  };

  return (
    <Modal open={open} onClose={onClose} title="Welcome to CarePath">
      <p className="mb-5 text-sm text-gray-500">
        Enter your name to personalize your clinic dashboard.
      </p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block text-sm font-semibold text-gray-700">
          Your name
          <input
            type="text"
            value={name}
            onChange={(event) => {
              setName(event.target.value);
              setError("");
            }}
            placeholder="Enter your name"
            autoFocus
            className="mt-1 block w-full rounded-xl border border-blue-100 bg-white/70 px-3 py-2.5 text-sm text-gray-800 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
          />
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          className="w-full rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700"
        >
          Continue
        </button>
      </form>
    </Modal>
  );
}
