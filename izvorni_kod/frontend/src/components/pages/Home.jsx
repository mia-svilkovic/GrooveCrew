import AddVinyl from "../AddVinyl" ;
import AllVinyls from "../AllVinyls" ;
import { useUser } from "../../contexts/UserContext"; // Import the user context


export default function Home() {
  const { user } = useUser();
  if (!user) return (
    <div>
      { <AllVinyls/> }
    </div>
  ) ;
  return (
    <div>
      { <AllVinyls/> }
      <AddVinyl/>
    </div>
  );
}
