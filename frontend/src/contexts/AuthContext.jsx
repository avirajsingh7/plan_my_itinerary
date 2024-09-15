import { createContext, useContext, useState } from "react";

export const AuthContext = createContext();

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider(props) {
    const [authUser, setAuthUser] = useState(null);
    const [isLoggedin, setIsLoggedin] = useState(false);

    const value = {
        authUser, setAuthUser, isLoggedin, setIsLoggedin
    }
    return (
        <AuthContext.Provider value={value}>
            {props.children}
        </AuthContext.Provider>
    )
}