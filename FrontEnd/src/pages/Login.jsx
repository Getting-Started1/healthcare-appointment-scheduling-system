import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import "../styles/register.css";
import Navbar from "../components/Navbar";
import axios from "axios";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import { setUserInfo } from "../redux/reducers/rootSlice";
import jwt_decode from "jwt-decode";
import fetchData from "../helper/apiCall";

axios.defaults.baseURL = process.env.REACT_APP_SERVER_DOMAIN;

function Login() {
  const dispatch = useDispatch();
  const [formDetails, setFormDetails] = useState({
    email: "",
    password: "",
    role: "",
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const inputChange = (e) => {
    const { name, value } = e.target;
    setFormDetails({
      ...formDetails,
      [name]: value,
    });
  };

  const formSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const { email, password, role } = formDetails;

      // Validation
      if (!email || !password || !role) {
        throw new Error("All fields are required");
      }
      if (!["Admin", "Doctor", "Patient"].includes(role)) {
        throw new Error("Please select a valid role");
      }
      if (password.length < 6) {
        throw new Error("Password must be at least 6 characters");
      }

      // Make login request
      const { data } = await axios.post("/login", {
        email,
        password,
        role,
      });

      // Store token and decode
      localStorage.setItem("token", data.access_token);
      const decoded = jwt_decode(data.access_token);
      
      // Dispatch user info
      dispatch(setUserInfo({
        id: decoded.user_id,
        role: decoded.role
      }));

      // Fetch complete user data
      const userData = await fetchData(`/user/getuser/${decoded.user_id}`);
      dispatch(setUserInfo(userData));

      // Redirect based on role
      if (role === "Admin") {
        navigate("/dashboard/home");
      } else {
        navigate("/");
      }

      toast.success("Login successful");

    } catch (error) {
      console.error("Login error:", error);
      const errorMessage = error.response?.data?.detail || 
                         error.message || 
                         "Login failed";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <section className="register-section flex-center">
        <div className="register-container flex-center">
          <h2 className="form-heading">Sign In</h2>
          <form onSubmit={formSubmit} className="register-form">
            <input
              type="email"
              name="email"
              className="form-input"
              placeholder="Enter your email"
              value={formDetails.email}
              onChange={inputChange}
              required
            />
            <input
              type="password"
              name="password"
              className="form-input"
              placeholder="Enter your password"
              value={formDetails.password}
              onChange={inputChange}
              minLength="6"
              required
            />
            <select
              name="role"
              className="form-input"
              value={formDetails.role}
              onChange={inputChange}
              required
            >
              <option value="">Select Role</option>
              <option value="Admin">Admin</option>
              <option value="Doctor">Doctor</option>
              <option value="Patient">Patient</option>
            </select>
            <button 
              type="submit" 
              className="btn form-btn"
              disabled={loading}
            >
              {loading ? "Logging in..." : "Sign in"}
            </button>
          </form>
          <NavLink className="login-link" to={"/forgotpassword"}>
            Forgot Password
          </NavLink>
          <p>
            Not a user?{" "}
            <NavLink className="login-link" to={"/register"}>
              Register
            </NavLink>
          </p>
        </div>
      </section>
    </>
  );
}

export default Login;