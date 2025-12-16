import api from "./http";

export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const { data } = await api.post("/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data; // { access_token, ... }
}

export async function signup(name: string, email: string, password: string) {
  const { data } = await api.post("/auth/signup", { name, email, password });
  return data;
}
