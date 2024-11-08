import './Header.css';
import logo from '../pictures/logo.png';


function Header(){
    return (
        <header>
            <img src={logo} alt="logo"/>
        </header>
    );
}

export default Header