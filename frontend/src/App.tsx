// frontend/src/App.tsx
import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

import { login, signup, getMe, type CurrentUser } from "./api/signup";
import { getProjects, createProject } from "./api/projects";
import type { Project } from "./api/projects";
import { getIssues, createIssue, updateIssueStatus } from "./api/issues";
import type { Issue, Priority, IssueStatus } from "./api/issues";
import { getComments, createComment } from "./api/comments";
import type { Comment } from "./api/comments";
import {
  getMembers,
  addMember,
  type ProjectMember,
  type Role,
} from "./api/members";

// -------------------- LOGIN / SIGNUP --------------------

function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      setError("");
      if (mode === "signup") {
        await signup(name, email, password);
      }
      const data = await login(email, password);
      localStorage.setItem("access_token", data.access_token);
      onLogin();
    } catch {
      setError(mode === "login" ? "Login failed" : "Signup or login failed");
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "40px auto" }}>
      <h2>{mode === "login" ? "IssueHub Login" : "IssueHub Signup"}</h2>
      <form onSubmit={handleSubmit}>
        {mode === "signup" && (
          <div>
            <label>Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              type="text"
              required
            />
          </div>
        )}
        <div>
          <label>Email</label>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            required
          />
        </div>
        <div>
          <label>Password</label>
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
          />
        </div>
        <button type="submit">{mode === "login" ? "Login" : "Sign up"}</button>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </form>

      <p style={{ marginTop: 16 }}>
        {mode === "login" ? (
          <>
            Need an account?{" "}
            <button type="button" onClick={() => setMode("signup")}>
              Sign up
            </button>
          </>
        ) : (
          <>
            Already have an account?{" "}
            <button type="button" onClick={() => setMode("login")}>
              Log in
            </button>
          </>
        )}
      </p>
    </div>
  );
}

// -------------------- PROJECTS / ISSUES / MEMBERS --------------------

function ProjectsPage({ currentUser }: { currentUser: CurrentUser }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [name, setName] = useState("");
  const [key, setKey] = useState("");
  const [description, setDescription] = useState("");

  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [issuesLoading, setIssuesLoading] = useState(false);

  const [issueTitle, setIssueTitle] = useState("");
  const [issueDescription, setIssueDescription] = useState("");
  const [issuePriority, setIssuePriority] = useState<Priority>("medium");

  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [newComment, setNewComment] = useState("");

  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [memberEmail, setMemberEmail] = useState("");
  const [memberRole, setMemberRole] = useState<Role>("developer");

  useEffect(() => {
    async function load() {
      try {
        const data = await getProjects();
        setProjects(data);
      } catch (err: any) {
        if (axios.isAxiosError(err) && err.response?.status === 401) {
          localStorage.removeItem("access_token");
          window.location.reload();
        } else {
          setError("Failed to load projects");
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleCreateProject(e: React.FormEvent) {
    e.preventDefault();
    try {
      const p = await createProject({
        name,
        key,
        description: description || undefined,
      });
      setProjects((prev) => [...prev, p]);
      setName("");
      setKey("");
      setDescription("");
    } catch {
      alert("Failed to create project");
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    window.location.reload();
  }

  async function handleSelectProject(p: Project) {
    setSelectedProject(p);
    setIssues([]);
    setSelectedIssue(null);
    setComments([]);
    setMembers([]);
    setIssuesLoading(true);
    try {
      const [issuesData, membersData] = await Promise.all([
        getIssues(p.id),
        getMembers(p.id),
      ]);
      setIssues(issuesData);
      setMembers(membersData);
    } catch {
      alert("Failed to load project data");
    } finally {
      setIssuesLoading(false);
    }
  }

  async function handleCreateIssue(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedProject) return;
    try {
      const issue = await createIssue(selectedProject.id, {
        title: issueTitle,
        description: issueDescription || undefined,
        priority: issuePriority,
      });
      setIssues((prev) => [...prev, issue]);
      setIssueTitle("");
      setIssueDescription("");
      setIssuePriority("medium");
    } catch {
      alert("Failed to create issue");
    }
  }

  async function handleSelectIssue(issue: Issue) {
    setSelectedIssue(issue);
    setComments([]);
    setCommentsLoading(true);
    try {
      const data = await getComments(issue.id);
      setComments(data);
    } catch {
      alert("Failed to load comments");
    } finally {
      setCommentsLoading(false);
    }
  }

  async function handleAddComment(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedIssue || !newComment.trim()) return;
    try {
      const created = await createComment(selectedIssue.id, newComment.trim());
      setComments((prev) => [...prev, created]);
      setNewComment("");
    } catch {
      alert("Failed to add comment");
    }
  }

  async function handleStatusChange(issue: Issue, status: IssueStatus) {
    try {
      const updated = await updateIssueStatus(issue.id, status);
      setIssues((prev) => prev.map((i) => (i.id === issue.id ? updated : i)));
      if (selectedIssue?.id === issue.id) {
        setSelectedIssue(updated);
      }
    } catch {
      alert("Failed to update status");
    }
  }

  async function handleAddMember(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedProject || !memberEmail.trim()) return;
    try {
      const m = await addMember(selectedProject.id, {
        email: memberEmail.trim(),
        role: memberRole, // "developer" or "manager"
      });
      setMembers((prev) => [...prev, m]);
      setMemberEmail("");
      setMemberRole("developer");
    } catch {
      alert("Failed to add member");
    }
  }

  const isMaintainer =
    !!selectedProject &&
    members.some(
      (m) =>
        m.project_id === selectedProject.id &&
        m.user_id === currentUser.id &&
        m.role === "manager"
    );

  if (loading) return <p>Loading projects...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div className="page">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>Your Projects</h2>
        <button onClick={handleLogout}>Logout</button>
      </div>

      <form onSubmit={handleCreateProject} style={{ marginBottom: 24 }}>
        <h3>Create Project</h3>
        <div>
          <label>Name </label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Key </label>
          <input
            value={key}
            onChange={(e) => setKey(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Description </label>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <button type="submit">Add Project</button>
      </form>

      <div className="projects-layout">
        {/* LEFT: projects + members */}
        <div className="column">
          <h3>Projects</h3>
          {projects.length === 0 ? (
            <p>No projects yet.</p>
          ) : (
            <ul>
              {projects.map((p) => (
                <li
                  key={p.id}
                  style={{
                    cursor: "pointer",
                    fontWeight:
                      selectedProject?.id === p.id ? "bold" : "normal",
                  }}
                  onClick={() => handleSelectProject(p)}
                >
                  {p.name} ({p.key})
                </li>
              ))}
            </ul>
          )}

          {selectedProject && (
            <div style={{ marginTop: 24 }}>
              <h4>Members for {selectedProject.name}</h4>

              {members.length === 0 ? (
                <p>No members yet.</p>
              ) : (
                <ul>
                  {members.map((m) => (
                    <li key={m.id}>
                      User #{m.user_id} –{" "}
                      {m.role === "manager" ? "MAINTAINER" : "MEMBER"}
                    </li>
                  ))}
                </ul>
              )}

              <form onSubmit={handleAddMember} style={{ marginTop: 8 }}>
                <div>
                  <label>Email </label>
                  <input
                    value={memberEmail}
                    onChange={(e) => setMemberEmail(e.target.value)}
                    type="email"
                    required
                  />
                </div>
                <div>
                  <label>Role </label>
                  <select
                    value={memberRole}
                    onChange={(e) => setMemberRole(e.target.value as Role)}
                  >
                    <option value="developer">MEMBER</option>
                    <option value="manager">MAINTAINER</option>
                  </select>
                </div>
                <button type="submit">Add Member</button>
              </form>
            </div>
          )}
        </div>

        {/* RIGHT: issues + comments */}
        <div className="column">
          <h3>Issues</h3>

          {!selectedProject && <p>Select a project to see issues.</p>}

          {selectedProject && (
            <>
              {/* create issue */}
              <form onSubmit={handleCreateIssue} style={{ marginBottom: 16 }}>
                <h4>Create Issue for {selectedProject.name}</h4>
                <div>
                  <label>Title </label>
                  <input
                    value={issueTitle}
                    onChange={(e) => setIssueTitle(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label>Description </label>
                  <input
                    value={issueDescription}
                    onChange={(e) => setIssueDescription(e.target.value)}
                  />
                </div>
                <div>
                  <label>Priority </label>
                  <select
                    value={issuePriority}
                    onChange={(e) =>
                      setIssuePriority(e.target.value as Priority)
                    }
                  >
                    <option value="low">LOW</option>
                    <option value="medium">MEDIUM</option>
                    <option value="high">HIGH</option>
                  </select>
                </div>
                <button type="submit">Add Issue</button>
              </form>

              {/* issues list */}
              {issuesLoading ? (
                <p>Loading issues...</p>
              ) : issues.length === 0 ? (
                <p>No issues for this project.</p>
              ) : (
                <ul>
                  {issues.map((iss) => (
                    <li
                      key={iss.id}
                      style={{ cursor: "pointer", marginBottom: 8 }}
                      onClick={() => handleSelectIssue(iss)}
                    >
                      <strong>{iss.title}</strong>{" "}
                      <select
                        value={iss.status}
                        disabled={!isMaintainer}
                        onChange={(e) =>
                          handleStatusChange(iss, e.target.value as IssueStatus)
                        }
                      >
                        <option value="open">OPEN</option>
                        <option value="in_progress">IN PROGRESS</option>
                        <option value="closed">CLOSED</option>
                      </select>{" "}
                      {!isMaintainer && (
                        <span style={{ fontSize: 12 }}> (view only)</span>
                      )}{" "}
                      ({iss.priority}) – {iss.description}
                    </li>
                  ))}
                </ul>
              )}

              {/* comments section */}
              {selectedIssue && (
                <div style={{ marginTop: 24 }}>
                  <h4>Comments for: {selectedIssue.title}</h4>
                  {commentsLoading ? (
                    <p>Loading comments...</p>
                  ) : comments.length === 0 ? (
                    <p>No comments yet.</p>
                  ) : (
                    <ul>
                      {comments.map((c) => (
                        <li key={c.id}>{c.body}</li>
                      ))}
                    </ul>
                  )}

                  <form onSubmit={handleAddComment} style={{ marginTop: 8 }}>
                    <div>
                      <label>New comment </label>
                      <input
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                      />
                    </div>
                    <button type="submit">Add Comment</button>
                  </form>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// -------------------- ROOT APP --------------------

function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [loadingUser, setLoadingUser] = useState(false);

  useEffect(() => {
    async function loadMe() {
      if (!token) return;
      setLoadingUser(true);
      try {
        const me = await getMe();
        setCurrentUser(me);
      } catch {
        localStorage.removeItem("access_token");
        setToken(null);
      } finally {
        setLoadingUser(false);
      }
    }
    loadMe();
  }, [token]);

  if (!token) {
    return (
      <div className="app-root">
        <LoginPage
          onLogin={() => setToken(localStorage.getItem("access_token"))}
        />
      </div>
    );
  }

  if (loadingUser || !currentUser) {
    return (
      <div className="app-root">
        <p>Loading user...</p>
      </div>
    );
  }

  return (
    <div className="app-root">
      <ProjectsPage currentUser={currentUser} />
    </div>
  );
}

export default App;
