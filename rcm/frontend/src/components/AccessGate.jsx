import { useState } from "react";
import { Eye, EyeOff, HeartPulse, LockKeyhole, UserRound } from "lucide-react";
import api from "../api";

const inputClass = "mt-1.5 block w-full rounded-2xl border border-slate-200 bg-white/90 px-3.5 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-100";

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
    <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top_left,_rgba(36,79,192,0.12),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(30,41,59,0.08),_transparent_25%),linear-gradient(135deg,#f5f2ea_0%,#faf8f5_40%,#edf2ff_100%)] px-4 py-10">
      <div className="relative w-full max-w-5xl rounded-[30px] border border-white/60 bg-white/35 p-2 shadow-[0_30px_80px_rgba(15,23,42,0.12)] backdrop-blur-2xl">
        <div className="grid overflow-hidden rounded-[28px] bg-[#fbfaf7]/90 lg:grid-cols-[0.96fr_1.04fr]">
          <aside className="relative hidden overflow-hidden bg-gradient-to-br from-[#172554] via-[#244fc0] to-[#4d75d8] p-7 text-white lg:flex lg:flex-col lg:justify-between">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(255,255,255,0.16),_transparent_28%),radial-gradient(circle_at_bottom_left,_rgba(191,219,254,0.18),_transparent_32%)]" aria-hidden="true" />

            <div className="relative z-10 flex h-full flex-col justify-between">
              <div>
                <div className="mb-8 flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/20 bg-white/10 shadow-[0_18px_38px_rgba(15,23,42,0.18)] backdrop-blur-md">
                    <HeartPulse size={22} aria-hidden="true" />
                  </div>
                  <div>
                    <div className="text-xl font-bold tracking-tight">CarePath</div>
                    <div className="text-[10px] uppercase tracking-[0.24em] text-blue-100/80">Clinic Management</div>
                  </div>
                </div>

                <div className="max-w-xs">
                  <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-blue-100/80">
                    {setupRequired ? "Platform owner setup" : "Secure access"}
                  </p>
                  <h1 className="text-4xl font-black leading-[1.05] tracking-tight text-white">
                    {setupRequired ? "Create the owner account" : "Modern care operations"}
                  </h1>
                </div>
              </div>

              <div className="flex items-center justify-center py-4">
                <div className="relative h-64 w-64">
                  <div className="absolute left-7 top-10 h-28 w-28 rounded-[32%] border border-white/15 bg-white/8 shadow-[0_20px_50px_rgba(15,23,42,0.18)] backdrop-blur-md rotate-12" />
                  <div className="absolute right-7 top-2 h-24 w-24 rounded-[45%] border border-white/15 bg-white/8 shadow-[0_18px_42px_rgba(15,23,42,0.16)] backdrop-blur-md -rotate-12" />
                  <div className="absolute bottom-4 left-16 h-36 w-36 rounded-[30%] border border-white/15 bg-white/8 shadow-[0_22px_48px_rgba(15,23,42,0.18)] backdrop-blur-md rotate-8" />
                  <div className="absolute inset-x-9 bottom-8 rounded-[20px] border border-white/20 bg-white/10 px-4 py-3 text-center text-[10px] font-semibold tracking-[0.28em] text-blue-50 shadow-[0_18px_48px_rgba(15,23,42,0.18)] backdrop-blur-md">
                    CAREPATH
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-white/15 bg-white/8 px-4 py-3 text-sm text-blue-50 shadow-[0_18px_38px_rgba(15,23,42,0.12)] backdrop-blur-md">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-[10px] uppercase tracking-[0.22em] text-blue-100/70">Status</div>
                    <div className="mt-1 font-semibold">Secure access enabled</div>
                  </div>
                  <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-300 shadow-[0_0_12px_rgba(110,231,183,0.9)]" aria-hidden="true" />
                </div>
              </div>
            </div>
          </aside>

          <div className="bg-white/55 p-6 sm:p-8 lg:p-10">
            <div className="mb-7 flex items-center justify-between gap-3 lg:hidden">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-600 text-white shadow-[0_12px_26px_rgba(36,79,192,0.2)]">
                  <HeartPulse size={20} aria-hidden="true" />
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-900">CarePath</div>
                  <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">Clinic Management</div>
                </div>
              </div>
            </div>

            <div className="mb-8 rounded-[26px] border border-[#ece3d8] bg-white/70 p-5 shadow-[0_18px_40px_rgba(15,23,42,0.04)] backdrop-blur-md">
              <div className="mb-2 text-[11px] font-bold uppercase tracking-[0.22em] text-brand-600">
                {setupRequired ? "Platform owner setup" : "Secure access"}
              </div>
              <h2 className="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
                {setupRequired ? "Create the owner account" : "Sign in to CarePath"}
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                {setupRequired
                  ? "This first account owns the platform and manages the complete care workflow."
                  : "Use the account provided by your platform owner to continue."}
              </p>
            </div>

            <form onSubmit={submit} className="space-y-4">
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
                className="w-full rounded-2xl bg-gradient-to-r from-brand-600 to-brand-700 px-4 py-3.5 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(36,79,192,0.22)] transition duration-200 hover:brightness-[1.03] disabled:cursor-wait disabled:opacity-60"
              >
                {submitting ? "Please wait…" : setupRequired ? "Create owner account" : "Sign in"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </main>
  );
}