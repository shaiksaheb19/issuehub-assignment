// frontend/src/api/auth.ts
import api from "./http";

export async function login(email: string, password: string) {
  const params = new URLSearchParams();
  params.append("username", email);
  params.append("password", password);

  const { data } = await api.post("/auth/login", params, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function signup(name: string, email: string, password: string) {
  const { data } = await api.post("/auth/signup", {
    name,
    email,
    password,
  });
  return data;
}

export type CurrentUser = {
  id: number;
  name: string;
  email: string;
  created_at: string;
};

export async function getMe(): Promise<CurrentUser> {
  const { data } = await api.get("/auth/me");
  return data;
}
