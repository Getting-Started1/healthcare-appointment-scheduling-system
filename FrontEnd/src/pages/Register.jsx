import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import "../styles/register.css";
import Navbar from "../components/Navbar";
import toast from "react-hot-toast";
import api from "../service/api";

function Register() {
  const [file, setFile] = useState("");
  const [selectedRole, setSelectedRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [formDetails, setFormDetails] = useState({
    firstname: "",
    lastname: "",
    email: "",
    password: "",
    confpassword: "",
  });
  const navigate = useNavigate();

  const inputChange = (e) => {
    const { name, value } = e.target;
    setFormDetails({
      ...formDetails,
      [name]: value,
    });
  };

  const onUpload = async (element) => {
    if (!element) return;
    
    setLoading(true);
    try {
      if (
        element.type === "image/jpeg" ||
        element.type === "image/png" ||
        element.type === "image/jpg"
      ) {
        const data = new FormData();
        data.append("file", element);
        data.append("upload_preset", process.env.REACT_APP_CLOUDINARY_PRESET);
        data.append("cloud_name", process.env.REACT_APP_CLOUDINARY_CLOUD_NAME);
        
        const response = await fetch(process.env.REACT_APP_CLOUDINARY_BASE_URL, {
          method: "POST",
          body: data,
        });
        
        if (!response.ok) {
          throw new Error("Upload failed");
        }
        
        const result = await response.json();
        setFile(result.secure_url);
        toast.success("Image uploaded successfully");
      } else {
        throw new Error("Please select an image in JPEG or PNG format");
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  const formSubmit = async (e) => {
    e.preventDefault();
    
    if (loading) return;
    
    const { firstname, lastname, email, password, confpassword } = formDetails;
    
    // Frontend validation
    if (!firstname || !lastname || !email || !password || !confpassword || !selectedRole) {
      return toast.error("All fields are required");
    }
    
    if (firstname.length < 2) {
      return toast.error("First name must be at least 2 characters");
    }
    
    if (lastname.length < 2) {
      return toast.error("Last name must be at least 2 characters");
    }
    
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return toast.error("Please enter a valid email address");
    }
    
    if (password.length < 6) {
      return toast.error("Password must be at least 6 characters");
    }
    
    if (password !== confpassword) {
      return toast.error("Passwords do not match");
    }
    
    setLoading(true);
    
    try {
      const userData = {
        firstname,
        lastname,
        email,
        password,
        confpassword,
        role: selectedRole,
        profile_picture: file || null,
      };

      const response = await api.post("/auth/register", userData);
      
      if (response.status === 200 || response.status === 201) {
        toast.success("Registration successful!");
        navigate("/login");
      } else {
        throw new Error(response.data?.detail || "Registration failed");
      }
    } catch (error) {
      console.error("Registration error:", error);
      
      if (error.response) {
        // Handle backend validation errors
        if (error.response.status === 422) {
          const errors = error.response.data?.detail;
          if (Array.isArray(errors)) {
            errors.forEach(err => {
              toast.error(`${err.loc.join('.')}: ${err.msg}`);
            });
          } else {
            toast.error(errors || "Validation error");
          }
        } else {
          toast.error(error.response.data?.detail || "Registration failed");
        }
      } else {
        toast.error(error.message || "Network error");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <section className="register-section flex-center">
        <div className="register-container flex-center">
          <h2 className="form-heading">Sign Up</h2>
          <form onSubmit={formSubmit} className="register-form">
            <input
              type="text"
              name="firstname"
              className="form-input"
              placeholder="Enter your first name"
              value={formDetails.firstname}
              onChange={inputChange}
              minLength="2"
              required
            />
            <input
              type="text"
              name="lastname"
              className="form-input"
              placeholder="Enter your last name"
              value={formDetails.lastname}
              onChange={inputChange}
              minLength="2"
              required
            />
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
              type="file"
              onChange={(e) => onUpload(e.target.files[0])}
              name="profile-pic"
              id="profile-pic"
              className="form-input"
              accept="image/jpeg, image/png, image/jpg"
            />
            <input
              type="password"
              name="password"
              className="form-input"
              placeholder="Enter your password (min 6 characters)"
              value={formDetails.password}
              onChange={inputChange}
              minLength="6"
              required
            />
            <input
              type="password"
              name="confpassword"
              className="form-input"
              placeholder="Confirm your password"
              value={formDetails.confpassword}
              onChange={inputChange}
              minLength="6"
              required
            />
            <select
              name="role"
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="form-input"
              required
            >
              <option value="">Select Role</option>
              <option value="Patient">Patient</option>
              <option value="Doctor">Doctor</option>
              <option value="Admin">Admin</option>
            </select>

            <button
              type="submit"
              className="btn form-btn"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Processing...
                </>
              ) : (
                "Sign Up"
              )}
            </button>
          </form>
          <p>
            Already a user?{" "}
            <NavLink className="login-link" to={"/login"}>
              Log in
            </NavLink>
          </p>
        </div>
      </section>
    </>
  );
}

export default Register;