import React, { useEffect, useState } from "react";
import "../styles/profile.css";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import axios from "axios";
import toast from "react-hot-toast";
import { setLoading } from "../redux/reducers/rootSlice";
import { useDispatch, useSelector } from "react-redux";
import Loading from "../components/Loading";
import fetchData from "../helper/apiCall";
import jwt_decode from "jwt-decode";

axios.defaults.baseURL = process.env.REACT_APP_SERVER_DOMAIN;

function Profile() {
  const { user_id: userId } = jwt_decode(localStorage.getItem("token"));
  const dispatch = useDispatch();
  const { loading } = useSelector((state) => state.root);

  const [file, setFile] = useState("");
  const [formDetails, setFormDetails] = useState({
    name: "",
    email: "",
    phone: "",
    insurance_info: ""
  });

  const getUser = async () => {
    try {
      dispatch(setLoading(true));
      const temp = await fetchData(`/user/getuser/${userId}`);
      setFormDetails({
        name: temp.name || "",
        email: temp.email || "",
        phone: temp.phone || "",
        insurance_info: temp.insurance_info || ""
      });
      setFile(temp.pic);
    } catch (error) {
      toast.error("Failed to load profile");
    } finally {
      dispatch(setLoading(false));
    }
  };

  useEffect(() => {
    getUser();
  }, []);

  const inputChange = (e) => {
    const { name, value } = e.target;
    setFormDetails((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const formSubmit = async (e) => {
    e.preventDefault();
    const { name, email, phone, insurance_info } = formDetails;

    try {
      await toast.promise(
        axios.put(
          `/patients/${userId}`,
          { name, email, phone, insurance_info },
          {
            headers: {
              authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        ),
        {
          pending: "Updating profile...",
          success: "Profile updated successfully",
          error: "Unable to update profile",
        }
      );
    } catch (error) {
      toast.error("Unable to update profile");
    }
  };

  return (
    <>
      <Navbar />
      {loading ? (
        <Loading />
      ) : (
        <section className="register-section flex-center">
          <div className="profile-container flex-center">
            <h2 className="form-heading">Profile</h2>

            {file && (
              <img
                src={file}
                alt="profile"
                className="profile-pic"
              />
            )}

            <form onSubmit={formSubmit} className="register-form">
              <div className="form-same-row">
                <input
                  type="text"
                  name="name"
                  className="form-input"
                  placeholder="Full name"
                  value={formDetails.name}
                  onChange={inputChange}
                />

                <input
                  type="email"
                  name="email"
                  className="form-input"
                  placeholder="Email"
                  value={formDetails.email}
                  onChange={inputChange}
                />
              </div>

              <input
                type="text"
                name="phone"
                className="form-input"
                placeholder="Phone"
                value={formDetails.phone}
                onChange={inputChange}
              />

              <textarea
                name="insurance_info"
                className="form-input"
                placeholder="Insurance info"
                value={formDetails.insurance_info}
                onChange={inputChange}
                rows="2"
              />

              <button type="submit" className="btn form-btn">
                Update
              </button>
            </form>
          </div>
        </section>
      )}
      <Footer />
    </>
  );
}

export default Profile;
