import { Sidebar } from "./components/sidebar/sidebar.tsx"

export default function Home() {
  const pageContent = () => {
    return(  
      <h1>oi</h1>
    )};
    
  return (
    <Sidebar content={pageContent()}>

    </Sidebar>
  );
}
