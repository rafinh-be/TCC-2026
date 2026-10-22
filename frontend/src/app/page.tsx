import { Sidebar } from "./components/sidebar/sidebar.tsx"
import { HomeContent } from "./components/home/homeContent"

export default function Home() {
  return (
    <Sidebar content={<HomeContent />} />
  );
}
