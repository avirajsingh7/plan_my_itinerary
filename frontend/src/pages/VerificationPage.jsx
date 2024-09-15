import { useNavigate, useParams } from "react-router-dom";
import Loader from "../components/Loader";
import { useEffect } from "react";
import user from "../services/authentication";

export default function VerificationPage() {
    const navigate = useNavigate();
    const {token} = useParams();

    useEffect(() => {
        user.verify(token).then(() => {
            navigate("/");
        })
    }, []);
    return (
        <div className="w-screen h-screen m-auto">
            <Loader />
        </div>
    )
}