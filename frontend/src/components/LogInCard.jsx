export default function LogInCard() {
    function login(username, password) {
        fetch('/api/auth/login', {
            method:'POST',
            body: {
                username: username,
                password: password
            }
        })
        

    }
    return (
        <>
        <form>
            <div className="input-group">
                <input type="text" className="form-control"></input>
                <input type="text" className="form-control"></input>
                <button type="btn-primary" onClick={login}>Log In!</button>
            </div>
        </form>
        </>
        )
    }