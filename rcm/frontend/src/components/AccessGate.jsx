import { useState } from "react";
import { Eye, EyeOff, HeartPulse, LockKeyhole, UserRound } from "lucide-react";
import api from "../api";

const inputClass = "mt-2 block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:bg-white focus:ring-4 focus:ring-brand-100";

export default function AccessGate({ setupRequired, onAuthenticated }) {
  const [displayName, setDisplayName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setError("");

    if (setupRequired && password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      const endpoint = setupRequired ? "/auth/setup" : "/auth/login";
      const payload = setupRequired
        ? { display_name: displayName.trim(), username: username.trim().toLowerCase(), password }
        : { username: username.trim().toLowerCase(), password };
      const { data } = await api.post(endpoint, payload);
      onAuthenticated(data.user);
    } catch (requestError) {
      setError(requestError.response?.data?.error || "Could not connect to the account service.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-cover bg-center p-3 text-slate-900 sm:p-6 lg:p-10" style={{ backgroundImage: "linear-gradient(135deg, rgba(9, 35, 82, 0.84), rgba(23, 71, 168, 0.68)), url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=2200&q=85')" }}>
      <div className="mx-auto grid min-h-[calc(100svh-1.5rem)] max-w-6xl overflow-hidden rounded-[24px] bg-white shadow-[0_24px_70px_rgba(15,23,42,0.2)] sm:min-h-[calc(100svh-3rem)] sm:rounded-[28px] lg:grid-cols-[1.02fr_0.98fr] lg:min-h-[680px]">
        <aside className="relative overflow-hidden bg-cover bg-center px-6 py-8 text-white sm:px-12 sm:py-10 lg:px-14 lg:py-12" style={{ backgroundImage: "linear-gradient(145deg, rgba(23, 71, 168, 0.96), rgba(11, 42, 104, 0.82)), url('https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=1400&q=85')" }}>
          <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full border-[28px] border-white/10" aria-hidden="true" />
          <div className="absolute -bottom-32 -left-20 h-80 w-80 rounded-full border-[34px] border-white/10" aria-hidden="true" />
          <div className="relative flex h-full flex-col">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-[#1747a8] shadow-lg">
                <HeartPulse size={23} strokeWidth={2.4} aria-hidden="true" />
              </div>
              <div>
                <div className="text-xl font-bold tracking-tight">CarePath</div>
                <div className="text-[10px] font-medium uppercase tracking-[0.22em] text-blue-100">Clinic Management</div>
              </div>
            </div>

            <div className="my-auto max-w-md py-12 sm:py-16">
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-semibold text-blue-50">
                <span className="h-2 w-2 rounded-full bg-emerald-300" aria-hidden="true" />
                Secure workspace
              </div>
              <h1 className="max-w-sm text-4xl font-bold leading-tight tracking-tight sm:text-5xl">
                {setupRequired ? "Build your care workspace" : "Everything your clinic needs"}
              </h1>
              <p className="mt-5 max-w-sm text-sm leading-7 text-blue-100 sm:text-base">
                Manage patients, appointments, doctors, billing, and clinical operations from one focused workspace.
              </p>
            </div>

            <div className="flex items-center gap-3 border-t border-white/15 pt-5 text-sm text-blue-100">
              <LockKeyhole size={17} aria-hidden="true" />
              <span>Private, role-based access for your team</span>
            </div>
          </div>
        </aside>

        <section className="flex items-center bg-white px-6 py-9 sm:px-12 sm:py-12 lg:px-16 lg:py-14">
          <div className="w-full max-w-md">
            <div className="mb-9">
              <div className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-brand-600">
                {setupRequired ? "First-time setup" : "Welcome back"}
              </div>
              <h2 className="text-3xl font-bold tracking-tight text-slate-950">
                {setupRequired ? "Create owner account" : "Sign in to CarePath"}
              </h2>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                {setupRequired
                  ? "Set up the account that will manage your clinic platform."
                  : "Enter your account details to continue to your workspace."}
              </p>
            </div>

            <form onSubmit={submit} className="space-y-5">
              {setupRequired && (
                <label className="block text-sm font-semibold text-slate-700">
                  Full name
                  <span className="relative block">
                    <UserRound size={17} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" aria-hidden="true" />
                    <input
                      type="text"
                      value={displayName}
                      onChange={(event) => setDisplayName(event.target.value)}
                      autoComplete="name"
                      required
                      maxLength={100}
                      className={`${inputClass} pl-10`}
                    />
                  </span>
                </label>
              )}

              <label className="block text-sm font-semibold text-slate-700">
                Username
                <input
                  type="text"
                  value={username}
                  onChange={(event) => setUsername(event.target.value.toLowerCase())}
                  autoComplete="username"
                  required
                  minLength={3}
                  maxLength={50}
                  pattern="[a-z0-9][a-z0-9._-]{2,49}"
                  title="Use lowercase letters, numbers, dots, dashes, or underscores."
                  className={inputClass}
                />
              </label>

              <label className="block text-sm font-semibold text-slate-700">
                Password
                <span className="relative block">
                  <LockKeyhole size={17} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" aria-hidden="true" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    autoComplete={setupRequired ? "new-password" : "current-password"}
                    required
                    minLength={setupRequired ? 12 : undefined}
                    className={`${inputClass} pl-10 pr-11`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((visible) => !visible)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded-xl p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    title={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                  </button>
                </span>
              </label>

              {setupRequired && (
                <label className="block text-sm font-semibold text-slate-700">
                  Confirm password
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    autoComplete="new-password"
                    required
                    minLength={12}
                    className={inputClass}
                  />
                  <span className="mt-1 block text-xs font-normal text-slate-500">Use at least 12 characters.</span>
                </label>
              )}

              {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700">{error}</p>}

              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-xl bg-gradient-to-r from-brand-600 to-brand-700 px-4 py-3.5 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(36,79,192,0.22)] transition duration-200 hover:brightness-[1.03] disabled:cursor-wait disabled:opacity-60"
              >
                {submitting ? "Please wait…" : setupRequired ? "Create owner account" : "Sign in"}
              </button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}