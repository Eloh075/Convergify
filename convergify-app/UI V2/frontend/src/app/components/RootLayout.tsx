import { Outlet } from "react-router";
import { Header } from "./Header";

export function RootLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-[#F8FAFC]" style={{ fontFamily: "Inter, sans-serif" }}>
      <Header />
      <main className="flex-1 flex flex-col">
        <Outlet />
      </main>
    </div>
  );
}