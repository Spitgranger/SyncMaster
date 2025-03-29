import jwt from 'jsonwebtoken'

export function initializeUser() {
    let accessToken: any = null
    let idToken: any = null
    let isSignedIn = false;
    let role = null
    let username = null
    let userId = null
    let siteId = null


    if (isAuthenticated()) {
        accessToken = localStorage.getItem("accessToken");
        idToken = localStorage.getItem("idToken");
        const decodedToken: any = jwt.decode(idToken);
        isSignedIn = true;
        role = decodedToken["custom:role"];
        username = decodedToken["name"]
        userId = decodedToken["sub"]
        siteId = localStorage.getItem("siteId")

    }
    return {
        accessToken: accessToken,
        idToken: idToken,
        isSignedIn: isSignedIn,
        role: role,
        username: username,
        userId: userId,
        siteId: siteId
    }
}

export function isAuthenticated() {
    if (typeof window !== "undefined") {
        console.log(localStorage.getItem("idToken"));
        console.log(localStorage.getItem("accessToken"));

        if (localStorage.getItem("idToken") !== null && localStorage.getItem("accessToken") !== null && localStorage.getItem("siteId") !== null) {
            const token: any = localStorage.getItem("idToken")
            const decodedToken: any = jwt.decode(token);

            if (decodedToken.exp < Math.round(Date.now() / 1000)) {
                localStorage.removeItem("idToken")
                localStorage.removeItem("accessToken")
                localStorage.removeItem("siteId")
                return false
            }
            else {
                return true
            }
        }
        return false
    }
}