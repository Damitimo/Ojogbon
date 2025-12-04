"use client";

import { useState, useEffect, FormEvent } from "react";
import { FileText, Sparkles, Download, Edit, Plus, CheckCircle2, AlertCircle, Loader2, Settings, X, Key, History, Clock, Trash2, User, Briefcase, GraduationCap, Rocket, Zap, Mail } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const isLocalBackend = API_URL.startsWith("http://localhost") || API_URL.startsWith("http://127.0.0.1");

export default function Home() {
  const [profiles, setProfiles] = useState<string[]>([]);
  const [currentProfile, setCurrentProfile] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [jobDescription, setJobDescription] = useState("");
  const [generatedResume, setGeneratedResume] = useState<any>(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKeyConfigured, setApiKeyConfigured] = useState(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [maskedApiKey, setMaskedApiKey] = useState<string | null>(null);
  const [includeSummary, setIncludeSummary] = useState(false);
  const [includeProjects, setIncludeProjects] = useState(false);
  const [resumeHistory, setResumeHistory] = useState<Array<{
    id: string;
    timestamp: Date;
    jobDescription: string;
    resume: any;
    companyName?: string;
    profileName: string;
  }>>([]);
  const [showProfileEditor, setShowProfileEditor] = useState(false);
  const [profileData, setProfileData] = useState<any>(null);
  const [isNewProfile, setIsNewProfile] = useState(false);
  const [newProfileName, setNewProfileName] = useState("");
  const [editingProfileName, setEditingProfileName] = useState("");
  const [profileEditorError, setProfileEditorError] = useState<string | null>(null);

  const [showContactModal, setShowContactModal] = useState(false);
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactMessage, setContactMessage] = useState("");

  const [showHistoryDrawer, setShowHistoryDrawer] = useState(false);

  // Filter resume history by currently selected profile so histories don't leak across profiles
  const profileHistory = currentProfile
    ? resumeHistory.filter((item) => item.profileName === currentProfile)
    : [];

  useEffect(() => {
    loadProfiles();
    if (isLocalBackend) {
      checkApiKey();
    } else {
      setApiKeyConfigured(true);
    }
  }, []);

  const checkApiKey = async () => {
    try {
      const res = await fetch(`${API_URL}/api/api-key/status`);
      const data = await res.json();
      setApiKeyConfigured(data.configured);
      setMaskedApiKey(data.masked_key);
    } catch (err) {
      console.error("Failed to check API key status:", err);
    }
  };

  const saveApiKey = async () => {
    if (!apiKeyInput.trim()) {
      setError("Please enter an API key");
      return;
    }

    try {
      const res = await fetch(`${API_URL}/api/api-key`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKeyInput })
      });

      if (!res.ok) throw new Error("Failed to save API key");

      await checkApiKey(); // Refresh to get masked key
      setShowApiKeyModal(false);
      setApiKeyInput("");
      setError(null);
    } catch (err: any) {
      setError("Failed to save API key");
    }
  };

  const loadProfiles = async () => {
    try {
      console.log("Fetching profiles from:", `${API_URL}/api/profiles`);
      const res = await fetch(`${API_URL}/api/profiles`);
      const data = await res.json();
      console.log("Profiles loaded:", data.profiles);

      const loadedProfiles: string[] = data.profiles || [];
      setProfiles(loadedProfiles);

      if (loadedProfiles.length > 0) {
        const defaultProfile = loadedProfiles.includes("Tech Profile")
          ? "Tech Profile"
          : loadedProfiles[0];
        setCurrentProfile(defaultProfile);
      } else {
        setCurrentProfile(null);
      }

      setLoading(false);
    } catch (err) {
      console.error("Failed to load profiles:", err);
      setError("Failed to connect to backend. Please check that the API is reachable and the environment variable NEXT_PUBLIC_API_URL is set correctly.");
      setLoading(false);
    }
  };

  const handleGenerateResume = async () => {
    if (!currentProfile || !jobDescription.trim()) {
      setError("Please select a profile and enter a job description");
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/api/generate-resume`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile_name: currentProfile,
          job_description: jobDescription,
          extra_knowledge: "",
          experience_bullet_counts: {}
        })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to generate resume");
      }

      const data = await res.json();
      setGeneratedResume(data.resume);
      
      // Save to history
      const historyItem = {
        id: Date.now().toString(),
        timestamp: new Date(),
        jobDescription: jobDescription,
        resume: data.resume,
        companyName: extractCompanyName(jobDescription),
        profileName: currentProfile
      };
      
      setResumeHistory(prev => [historyItem, ...prev]);
    } catch (err: any) {
      console.error("Resume generation error:", err);
      setError(err.message || "Failed to generate resume");
    } finally {
      setGenerating(false);
    }
  };

  const extractCompanyName = (jd: string): string => {
    // Simple extraction - gets first capitalized word or "Company"
    const lines = jd.split('\n');
    for (const line of lines.slice(0, 5)) {
      const match = line.match(/\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b/);
      if (match) return match[1];
    }
    return "Company";
  };

  const handleContactSubmit = (e: FormEvent) => {
    e.preventDefault();

    const subject = `Ojogbon Contact from ${contactName || "User"}`;
    const bodyLines = [
      `Name: ${contactName || "N/A"}`,
      `Email: ${contactEmail || "N/A"}`,
      "",
      "Message:",
      contactMessage || "",
    ];

    const mailtoLink = `mailto:timothy.o.ojo@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(bodyLines.join("\n"))}`;

    if (typeof window !== "undefined") {
      window.location.href = mailtoLink;
    }

    setShowContactModal(false);
  };

  const loadProfileData = async (profileName: string) => {
    try {
      const res = await fetch(`${API_URL}/api/profiles/${profileName}`);
      const data = await res.json();
      setProfileData(data.profile);
      setEditingProfileName(profileName);
      setShowProfileEditor(true);
    } catch (err) {
      console.error("Failed to load profile:", err);
      setError("Failed to load profile data");
    }
  };

  const createNewProfile = () => {
    const blankProfile = {
      personal_info: {
        name: "",
        email: "",
        phone: "",
        location: "",
        linkedin: "",
        github: ""
      },
      summary: "",
      my_story: "",
      education: [],
      experience: [],
      projects: [],
      skills: {
        technical: [],
        languages: [],
        tools: [],
        soft_skills: []
      },
      certifications: [],
      awards: []
    };
    
    setProfileData(blankProfile);
    setIsNewProfile(true);
    setNewProfileName("");
    setEditingProfileName("");
    setProfileEditorError(null);
    setShowProfileEditor(true);
  };

  const saveProfileData = async () => {
    const profileName = isNewProfile ? newProfileName : editingProfileName;
    
    if (!profileName || !profileName.trim()) {
      setProfileEditorError("Please enter a profile name");
      return;
    }

    if (!profileData) {
      setProfileEditorError("Profile data is missing");
      return;
    }

    try {
      setProfileEditorError(null);
      const res = await fetch(`${API_URL}/api/profiles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile_name: profileName,
          profile: profileData
        })
      });

      if (!res.ok) throw new Error("Failed to save profile");

      setShowProfileEditor(false);
      setIsNewProfile(false);
      setProfileData(null);
      setNewProfileName("");
      setEditingProfileName("");
      setProfileEditorError(null);
      setError(null);
      
      // Reload profiles list
      await loadProfiles();
      
      // Select the newly created/updated profile
      setCurrentProfile(profileName);
      
      alert(`Profile "${profileName}" saved successfully!`);
    } catch (err: any) {
      console.error("Save error:", err);
      setProfileEditorError(err?.message || "Failed to save profile");
    }
  };

  const handleExportDocx = async () => {
    if (!generatedResume) return;

    try {
      // Filter sections based on user selection
      const filteredResume = { ...generatedResume };
      
      if (!includeSummary) {
        delete filteredResume.summary;
      }
      
      if (!includeProjects) {
        delete filteredResume.projects;
      }

      const res = await fetch(`${API_URL}/api/export/docx`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(filteredResume)
      });

      if (!res.ok) throw new Error("Export failed");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "resume.docx";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("Export error:", err);
      setError("Failed to export resume");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col relative">
      {/* Top Navigation Bar */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="w-full px-4 sm:px-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between py-3 sm:h-16 space-y-3 sm:space-y-0">
            {/* Left: Logo & Title */}
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Ojogbon</h1>
                <p className="text-xs text-gray-500">Intelligent Resume Crafting</p>
              </div>
            </div>

            {/* Right: Profile Controls */}
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 sm:ml-auto w-full sm:w-auto justify-start sm:justify-end">
              {loading ? (
                <div className="text-sm text-gray-500">Loading...</div>
              ) : (
                <>
                  {/* Debug: Show profile count */}
                  {profiles.length === 0 && (
                    <div className="text-xs text-red-600 mr-2">No profiles found</div>
                  )}
                  
                  {/* Profile Dropdown */}
                  <select
                    className="h-10 pl-3 pr-8 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white w-full sm:w-auto min-w-[150px] sm:min-w-[200px] max-w-[180px] sm:max-w-none cursor-pointer hover:bg-gray-50 transition-colors"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                      backgroundPosition: 'right 0.5rem center',
                      backgroundRepeat: 'no-repeat',
                      backgroundSize: '1.5em 1.5em',
                      appearance: 'none',
                      WebkitAppearance: 'none',
                      MozAppearance: 'none'
                    }}
                    value={currentProfile || ""}
                    onChange={(e) => setCurrentProfile(e.target.value || null)}
                  >
                    <option value="">Select Profile ({profiles.length} available)</option>
                    {profiles.map((profile) => (
                      <option key={profile} value={profile}>
                        {profile}
                      </option>
                    ))}
                  </select>

                  {/* Edit Profile Button */}
                  <button
                    onClick={() => {
                      if (currentProfile) {
                        loadProfileData(currentProfile);
                      }
                    }}
                    className="h-10 px-4 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
                    disabled={!currentProfile}
                    title="Edit your profile information"
                  >
                    <Edit className="h-4 w-4" />
                    <span className="hidden md:inline">Edit Profile</span>
                  </button>

                  {/* New Profile Button */}
                  <button 
                    onClick={createNewProfile}
                    className="h-10 px-4 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors shadow-sm"
                    title="Create a new profile"
                  >
                    <Plus className="h-4 w-4" />
                    <span>New Profile</span>
                  </button>

                  {/* Mobile History Button (top-right trigger) */}
                  <button
                    type="button"
                    onClick={() => setShowHistoryDrawer(!showHistoryDrawer)}
                    className="sm:hidden h-10 w-10 flex items-center justify-center text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                    title="View resume history"
                  >
                    <History className="h-4 w-4" />
                  </button>

                  {/* Settings Button (local development only) */}
                  {isLocalBackend && (
                    <button
                      onClick={() => setShowApiKeyModal(true)}
                      className="h-10 px-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center transition-colors relative"
                      title="API Settings"
                    >
                      <Settings className="h-4 w-4" />
                      {!apiKeyConfigured && (
                        <div className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full border-2 border-white"></div>
                      )}
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile History Panel (top-right overlay) */}
      {showHistoryDrawer && (
        <div className="sm:hidden fixed top-16 right-4 z-40 w-72 max-w-[90vw] bg-white border border-gray-200 rounded-lg shadow-lg">
          <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <History className="h-4 w-4 text-gray-600" />
              <h2 className="font-semibold text-gray-900 text-sm">Resume History</h2>
            </div>
            <button
              onClick={() => setShowHistoryDrawer(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="max-h-80 overflow-y-auto p-3 space-y-2">
            {profileHistory.length === 0 ? (
              <div className="text-center py-6 text-gray-500">
                <History className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                <p className="text-sm">No resumes generated yet</p>
                <p className="text-xs mt-1">Your history will appear here</p>
              </div>
            ) : (
              profileHistory.map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    setJobDescription(item.jobDescription);
                    setGeneratedResume(item.resume);
                    setShowHistoryDrawer(false);
                  }}
                  className="p-3 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer border border-gray-200 transition-colors"
                >
                  <div className="flex items-start justify-between mb-1.5">
                    <h3 className="font-medium text-sm text-gray-900 line-clamp-1">
                      {item.companyName || "Company"}
                    </h3>
                    <Clock className="h-3 w-3 text-gray-400 flex-shrink-0 ml-2" />
                  </div>
                  <p className="text-xs text-gray-500 line-clamp-2 mb-1.5">
                    {item.jobDescription.substring(0, 80)}...
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(item.timestamp).toLocaleDateString()} {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Main Content with History Sidebar */}
      <div className="flex flex-col lg:flex-row flex-1">
        {/* History Sidebar - desktop only; mobile uses top-right panel */}
        <aside className="hidden lg:block w-80 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <History className="h-5 w-5 text-gray-600" />
              <h2 className="font-semibold text-gray-900">Resume History</h2>
            </div>
          </div>
          
          <div className="p-4 space-y-2">
            {profileHistory.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <History className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p className="text-sm">No resumes generated yet</p>
                <p className="text-xs mt-1">Your history will appear here</p>
              </div>
            ) : (
              profileHistory.map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    setJobDescription(item.jobDescription);
                    setGeneratedResume(item.resume);
                  }}
                  className="p-3 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer border border-gray-200 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-sm text-gray-900 line-clamp-1">
                      {item.companyName || "Company"}
                    </h3>
                    <Clock className="h-3 w-3 text-gray-400 flex-shrink-0 ml-2" />
                  </div>
                  <p className="text-xs text-gray-500 line-clamp-2 mb-2">
                    {item.jobDescription.substring(0, 80)}...
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(item.timestamp).toLocaleDateString()} {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              ))
            )}
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto px-6 py-8">

        {/* Profile Editor Modal */}
        {showProfileEditor && profileData && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full p-6 my-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-2">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    {isNewProfile ? <Plus className="h-5 w-5 text-blue-600" /> : <Edit className="h-5 w-5 text-blue-600" />}
                  </div>
                  <h2 className="text-xl font-semibold">
                    {isNewProfile ? "Create New Profile" : `Edit Profile: ${currentProfile}`}
                  </h2>
                </div>
                <button
                  onClick={() => {
                    setShowProfileEditor(false);
                    setProfileData(null);
                    setIsNewProfile(false);
                    setNewProfileName("");
                    setEditingProfileName("");
                    setProfileEditorError(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Profile Name Input */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Profile Name *</label>
                <input
                  type="text"
                  value={isNewProfile ? newProfileName : editingProfileName}
                  onChange={(e) => {
                    if (isNewProfile) {
                      setNewProfileName(e.target.value);
                    } else {
                      setEditingProfileName(e.target.value);
                    }
                  }}
                  placeholder="e.g., John Doe, Marketing Profile, etc."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {isNewProfile 
                    ? "This will be the name of your profile file" 
                    : "Changing the name will create a new profile and keep the old one"
                  }
                </p>
                {profileEditorError && (
                  <p className="text-xs text-red-600 mt-1">{profileEditorError}</p>
                )}
              </div>

              <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2">
                {/* Personal Info */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 flex items-center space-x-2">
                    <User className="h-5 w-5 text-gray-600" />
                    <span>Personal Information</span>
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                      <input
                        type="text"
                        value={profileData.personal_info?.name || ""}
                        onChange={(e) => setProfileData({
                          ...profileData,
                          personal_info: { ...profileData.personal_info, name: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                      <input
                        type="email"
                        value={profileData.personal_info?.email || ""}
                        onChange={(e) => setProfileData({
                          ...profileData,
                          personal_info: { ...profileData.personal_info, email: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                      <input
                        type="tel"
                        value={profileData.personal_info?.phone || ""}
                        onChange={(e) => setProfileData({
                          ...profileData,
                          personal_info: { ...profileData.personal_info, phone: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                      <input
                        type="text"
                        value={profileData.personal_info?.location || ""}
                        onChange={(e) => setProfileData({
                          ...profileData,
                          personal_info: { ...profileData.personal_info, location: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">LinkedIn URL</label>
                      <input
                        type="url"
                        value={profileData.personal_info?.linkedin || ""}
                        onChange={(e) => setProfileData({
                          ...profileData,
                          personal_info: { ...profileData.personal_info, linkedin: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">GitHub URL</label>
                      <input
                        type="url"
                        value={profileData.personal_info?.github || ""}
                        onChange={(e) => setProfileData({
                          ...profileData,
                          personal_info: { ...profileData.personal_info, github: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                    </div>
                  </div>
                </div>

                {/* Professional Summary */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-gray-600" />
                    <span>Professional Summary</span>
                  </h3>
                  <textarea
                    value={profileData.summary || ""}
                    onChange={(e) => setProfileData({ ...profileData, summary: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    placeholder="Brief professional summary..."
                  />
                </div>

                {/* Experience Section */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-lg flex items-center space-x-2">
                      <Briefcase className="h-5 w-5 text-gray-600" />
                      <span>Work Experience</span>
                    </h3>
                    <button
                      onClick={() => {
                        const newExp = {
                          title: "",
                          company: "",
                          location: "",
                          start_date: "",
                          end_date: "",
                          description: [""],
                          skills_used: []
                        };
                        setProfileData({
                          ...profileData,
                          experience: [...(profileData.experience || []), newExp]
                        });
                      }}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Add Experience</span>
                    </button>
                  </div>
                  
                  {profileData.experience?.map((exp: any, idx: number) => (
                    <div key={idx} className="mb-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
                      <div className="flex justify-between items-start mb-3">
                        <span className="font-medium text-sm text-gray-700">Experience #{idx + 1}</span>
                        <button
                          onClick={() => {
                            const newExp = profileData.experience.filter((_: any, i: number) => i !== idx);
                            setProfileData({ ...profileData, experience: newExp });
                          }}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <input
                          type="text"
                          placeholder="Job Title"
                          value={exp.title || ""}
                          onChange={(e) => {
                            const newExp = [...profileData.experience];
                            newExp[idx].title = e.target.value;
                            setProfileData({ ...profileData, experience: newExp });
                          }}
                          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <input
                          type="text"
                          placeholder="Company"
                          value={exp.company || ""}
                          onChange={(e) => {
                            const newExp = [...profileData.experience];
                            newExp[idx].company = e.target.value;
                            setProfileData({ ...profileData, experience: newExp });
                          }}
                          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <input
                          type="text"
                          placeholder="Location"
                          value={exp.location || ""}
                          onChange={(e) => {
                            const newExp = [...profileData.experience];
                            newExp[idx].location = e.target.value;
                            setProfileData({ ...profileData, experience: newExp });
                          }}
                          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <div className="grid grid-cols-2 gap-2">
                          <input
                            type="text"
                            placeholder="Start Date"
                            value={exp.start_date || ""}
                            onChange={(e) => {
                              const newExp = [...profileData.experience];
                              newExp[idx].start_date = e.target.value;
                              setProfileData({ ...profileData, experience: newExp });
                            }}
                            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                          <input
                            type="text"
                            placeholder="End Date"
                            value={exp.end_date || ""}
                            onChange={(e) => {
                              const newExp = [...profileData.experience];
                              newExp[idx].end_date = e.target.value;
                              setProfileData({ ...profileData, experience: newExp });
                            }}
                            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                      <div className="mt-3">
                        <label className="block text-xs font-medium text-gray-600 mb-1">Responsibilities (one per line)</label>
                        <textarea
                          placeholder="• Achieved X% improvement&#10;• Led team of Y people&#10;• Developed Z feature"
                          value={exp.description?.join('\n') || ""}
                          onChange={(e) => {
                            const newExp = [...profileData.experience];
                            newExp[idx].description = e.target.value.split('\n');
                            setProfileData({ ...profileData, experience: newExp });
                          }}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Education Section */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-lg flex items-center space-x-2">
                      <GraduationCap className="h-5 w-5 text-gray-600" />
                      <span>Education</span>
                    </h3>
                    <button
                      onClick={() => {
                        const newEdu = {
                          degree: "",
                          institution: "",
                          location: "",
                          start_date: "",
                          end_date: "",
                          gpa: "",
                          achievements: []
                        };
                        setProfileData({
                          ...profileData,
                          education: [...(profileData.education || []), newEdu]
                        });
                      }}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Add Education</span>
                    </button>
                  </div>
                  
                  {profileData.education?.map((edu: any, idx: number) => (
                    <div key={idx} className="mb-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
                      <div className="flex justify-between items-start mb-3">
                        <span className="font-medium text-sm text-gray-700">Education #{idx + 1}</span>
                        <button
                          onClick={() => {
                            const newEdu = profileData.education.filter((_: any, i: number) => i !== idx);
                            setProfileData({ ...profileData, education: newEdu });
                          }}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <input
                          type="text"
                          placeholder="Degree (e.g., Bachelor of Science in Computer Science)"
                          value={edu.degree || ""}
                          onChange={(e) => {
                            const newEdu = [...profileData.education];
                            newEdu[idx].degree = e.target.value;
                            setProfileData({ ...profileData, education: newEdu });
                          }}
                          className="col-span-2 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <input
                          type="text"
                          placeholder="Institution"
                          value={edu.institution || ""}
                          onChange={(e) => {
                            const newEdu = [...profileData.education];
                            newEdu[idx].institution = e.target.value;
                            setProfileData({ ...profileData, education: newEdu });
                          }}
                          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <input
                          type="text"
                          placeholder="Location"
                          value={edu.location || ""}
                          onChange={(e) => {
                            const newEdu = [...profileData.education];
                            newEdu[idx].location = e.target.value;
                            setProfileData({ ...profileData, education: newEdu });
                          }}
                          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <div className="grid grid-cols-2 gap-2">
                          <input
                            type="text"
                            placeholder="Start Date"
                            value={edu.start_date || ""}
                            onChange={(e) => {
                              const newEdu = [...profileData.education];
                              newEdu[idx].start_date = e.target.value;
                              setProfileData({ ...profileData, education: newEdu });
                            }}
                            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                          <input
                            type="text"
                            placeholder="End Date"
                            value={edu.end_date || ""}
                            onChange={(e) => {
                              const newEdu = [...profileData.education];
                              newEdu[idx].end_date = e.target.value;
                              setProfileData({ ...profileData, education: newEdu });
                            }}
                            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <input
                          type="text"
                          placeholder="GPA (optional)"
                          value={edu.gpa || ""}
                          onChange={(e) => {
                            const newEdu = [...profileData.education];
                            newEdu[idx].gpa = e.target.value;
                            setProfileData({ ...profileData, education: newEdu });
                          }}
                          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Projects Section */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-lg flex items-center space-x-2">
                      <Rocket className="h-5 w-5 text-gray-600" />
                      <span>Projects</span>
                    </h3>
                    <button
                      onClick={() => {
                        const newProject = {
                          name: "",
                          description: "",
                          technologies: [],
                          achievements: [],
                          url: ""
                        };
                        setProfileData({
                          ...profileData,
                          projects: [...(profileData.projects || []), newProject]
                        });
                      }}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Add Project</span>
                    </button>
                  </div>
                  
                  {profileData.projects?.map((project: any, idx: number) => (
                    <div key={idx} className="mb-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
                      <div className="flex justify-between items-start mb-3">
                        <span className="font-medium text-sm text-gray-700">Project #{idx + 1}</span>
                        <button
                          onClick={() => {
                            const newProjects = profileData.projects.filter((_: any, i: number) => i !== idx);
                            setProfileData({ ...profileData, projects: newProjects });
                          }}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="space-y-3">
                        <input
                          type="text"
                          placeholder="Project Name"
                          value={project.name || ""}
                          onChange={(e) => {
                            const newProjects = [...profileData.projects];
                            newProjects[idx].name = e.target.value;
                            setProfileData({ ...profileData, projects: newProjects });
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <textarea
                          placeholder="Project Description"
                          value={project.description || ""}
                          onChange={(e) => {
                            const newProjects = [...profileData.projects];
                            newProjects[idx].description = e.target.value;
                            setProfileData({ ...profileData, projects: newProjects });
                          }}
                          rows={2}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <input
                          type="text"
                          placeholder="Technologies (comma-separated: React, Node.js, MongoDB)"
                          value={project.technologies?.join(', ') || ""}
                          onChange={(e) => {
                            const newProjects = [...profileData.projects];
                            newProjects[idx].technologies = e.target.value.split(',').map((t: string) => t.trim());
                            setProfileData({ ...profileData, projects: newProjects });
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Skills Section */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 flex items-center space-x-2">
                    <Zap className="h-5 w-5 text-gray-600" />
                    <span>Skills</span>
                  </h3>
                  <div className="space-y-3">
                    <div className="grid grid-cols-4 gap-2">
                      <div className="col-span-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Category Name</label>
                        <input
                          type="text"
                          placeholder="e.g., Technical"
                          defaultValue="Technical Skills"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div className="col-span-3">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Skills (comma-separated)</label>
                        <input
                          type="text"
                          placeholder="e.g., Python, JavaScript, React, SQL"
                          value={profileData.skills?.technical?.join(', ') || ""}
                          onChange={(e) => setProfileData({
                            ...profileData,
                            skills: {
                              ...profileData.skills,
                              technical: e.target.value.split(',').map((s: string) => s.trim()).filter((s: string) => s)
                            }
                          })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-4 gap-2">
                      <div className="col-span-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Category Name</label>
                        <input
                          type="text"
                          placeholder="e.g., Languages"
                          defaultValue="Languages"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div className="col-span-3">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Skills (comma-separated)</label>
                        <input
                          type="text"
                          placeholder="e.g., English (Native), Spanish (Fluent)"
                          value={profileData.skills?.languages?.join(', ') || ""}
                          onChange={(e) => setProfileData({
                            ...profileData,
                            skills: {
                              ...profileData.skills,
                              languages: e.target.value.split(',').map((s: string) => s.trim()).filter((s: string) => s)
                            }
                          })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-4 gap-2">
                      <div className="col-span-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Category Name</label>
                        <input
                          type="text"
                          placeholder="e.g., Tools"
                          defaultValue="Tools & Frameworks"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div className="col-span-3">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Skills (comma-separated)</label>
                        <input
                          type="text"
                          placeholder="e.g., Git, Docker, AWS, VS Code"
                          value={profileData.skills?.tools?.join(', ') || ""}
                          onChange={(e) => setProfileData({
                            ...profileData,
                            skills: {
                              ...profileData.skills,
                              tools: e.target.value.split(',').map((s: string) => s.trim()).filter((s: string) => s)
                            }
                          })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                    
                    <p className="text-xs text-gray-500 mt-2">
                      You can customize the category names to fit your profession (e.g., change "Technical Skills" to "Clinical Skills" for healthcare, or "Design Skills" for creative roles). Each category accepts comma-separated skills.
                    </p>
                  </div>
                </div>
              </div>

              {/* Footer Actions */}
              <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setShowProfileEditor(false);
                    setProfileData(null);
                    setIsNewProfile(false);
                    setNewProfileName("");
                    setEditingProfileName("");
                    setProfileEditorError(null);
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={saveProfileData}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {isNewProfile ? "Create Profile" : "Save Profile"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* API Key Modal (local development only) */}
        {isLocalBackend && showApiKeyModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <Key className="h-5 w-5 text-blue-600" />
                  </div>
                  <h2 className="text-xl font-semibold">API Settings</h2>
                </div>
                <button
                  onClick={() => {
                    setShowApiKeyModal(false);
                    setApiKeyInput("");
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="mb-4">
                {apiKeyConfigured && maskedApiKey ? (
                  <>
                    <p className="text-sm text-gray-600 mb-4">
                      Your Claude API key is configured and ready to use.
                    </p>
                    
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Claude API Key
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={maskedApiKey}
                        readOnly
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm text-gray-600 cursor-not-allowed"
                      />
                      <div className="flex items-center space-x-1 text-green-600">
                        <CheckCircle2 className="h-5 w-5" />
                      </div>
                    </div>
                    
                    <p className="text-xs text-gray-500 mt-2">
                      API key ending in <code className="bg-gray-100 px-1 py-0.5 rounded">{maskedApiKey.slice(-4)}</code>
                    </p>
                  </>
                ) : (
                  <>
                    <p className="text-sm text-gray-600 mb-4">
                      Enter your Claude API key to enable AI resume generation. Your key is stored securely.
                    </p>
                    
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Claude API Key
                    </label>
                    <input
                      type="password"
                      value={apiKeyInput}
                      onChange={(e) => setApiKeyInput(e.target.value)}
                      placeholder="sk-ant-..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') saveApiKey();
                      }}
                    />
                    
                    <p className="text-xs text-gray-500 mt-2">
                      Get your API key from{" "}
                      <a
                        href="https://console.anthropic.com/settings/keys"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        Anthropic Console
                      </a>
                    </p>
                  </>
                )}
              </div>

              <div className="flex items-center justify-end">
                {apiKeyConfigured && maskedApiKey ? (
                  <button
                    onClick={() => {
                      setShowApiKeyModal(false);
                    }}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Close
                  </button>
                ) : (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setShowApiKeyModal(false);
                        setApiKeyInput("");
                      }}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={saveApiKey}
                      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Save API Key
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Welcome Message */}
        {!currentProfile && (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center border border-gray-200 w-full max-w-4xl mx-auto">
            <div className="flex justify-center mb-4">
              <div className="bg-blue-100 p-4 rounded-full">
                <Sparkles className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <h2 className="text-2xl font-bold mb-4">Welcome to AI Resume Generator</h2>
            <p className="text-gray-600 mb-6">
              Create or load a profile to get started with generating tailored resumes.
            </p>
            <div className="text-left max-w-2xl mx-auto bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-semibold mb-3 flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <span>Getting Started:</span>
              </h3>
              <ol className="space-y-2 text-gray-700">
                <li className="flex items-start space-x-2">
                  <span className="font-semibold text-blue-600">1.</span>
                  <span>Click <strong>"New Profile"</strong> in the top navigation bar</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="font-semibold text-blue-600">2.</span>
                  <span>Fill in your professional information (education, experience, skills, etc.)</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="font-semibold text-blue-600">3.</span>
                  <span>Save your profile with a unique name</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="font-semibold text-blue-600">4.</span>
                  <span>Select your profile from the dropdown and start generating tailored resumes!</span>
                </li>
              </ol>
              <div className="mt-4 p-3 bg-white border border-blue-300 rounded-md flex items-start space-x-2">
                <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-600">
                  <strong>Tip:</strong> Each user should create their own profile. This allows multiple people to use the software with their own information.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* API Key Warning (local development only) */}
        {isLocalBackend && !apiKeyConfigured && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg mb-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5" />
              <span>Claude API key not configured. Click the settings icon to add your API key.</span>
            </div>
            <button
              onClick={() => setShowApiKeyModal(true)}
              className="px-3 py-1 text-sm font-medium text-yellow-800 bg-yellow-100 rounded-md hover:bg-yellow-200 transition-colors"
            >
              Configure Now
            </button>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-center space-x-2">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        )}

        {/* Resume Generator */}
        {currentProfile && (
          <>
            {/* Status Badge */}
            <div className="mb-6 flex items-center justify-between bg-green-50 border border-green-200 rounded-lg px-4 py-3">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <span className="text-sm text-gray-700">Profile Loaded: <strong className="text-gray-900">{currentProfile}</strong></span>
              </div>
              <span className="text-xs text-green-700 font-medium">Ready to generate</span>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 w-full">
              {/* Input Card */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <Sparkles className="h-5 w-5 text-blue-600" />
                  </div>
                  <h2 className="text-lg font-semibold text-gray-900">Job Description</h2>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Paste the full job description below and AI will tailor your resume to match it perfectly.
                </p>

                <textarea
                  className="w-full h-72 p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                  placeholder="Paste the full job description here...

The AI will analyze:
• Required skills and qualifications
• Company culture and values
• Responsibilities and expectations
• Technical requirements

Then generate a tailored resume that highlights your relevant experience."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  disabled={generating}
                />
                
                {/* Section Controls */}
                <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-xs font-semibold text-gray-700 mb-2">Include Sections:</p>
                  <div className="flex flex-wrap gap-4">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={includeSummary}
                        onChange={(e) => setIncludeSummary(e.target.checked)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">Professional Summary</span>
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={includeProjects}
                        onChange={(e) => setIncludeProjects(e.target.checked)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">Projects</span>
                    </label>
                  </div>
                </div>

                <button 
                  className="mt-4 w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm flex items-center justify-center space-x-2"
                  onClick={handleGenerateResume}
                  disabled={generating || !jobDescription.trim()}
                >
                  {generating ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Generating Resume...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5" />
                      <span>Generate Tailored Resume</span>
                    </>
                  )}
                </button>
              </div>

              {/* Preview Card */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <div className="bg-green-100 p-2 rounded-lg">
                    <FileText className="h-5 w-5 text-green-600" />
                  </div>
                  <h2 className="text-lg font-semibold text-gray-900">Resume Preview</h2>
                </div>
              {generatedResume ? (
                <div className="flex flex-col h-full">
                  <div className="flex items-center space-x-2 text-green-600 font-semibold mb-4">
                    <CheckCircle2 className="h-5 w-5" />
                    <span>Resume Generated Successfully!</span>
                  </div>
                  <div className="flex-1 border border-gray-200 rounded-lg p-4 bg-gray-50 overflow-y-auto mb-4" style={{ maxHeight: '400px' }}>
                    <div className="space-y-2">
                      <h3 className="font-bold text-lg">{generatedResume.personal_info?.name || "Name"}</h3>
                      <p className="text-sm text-gray-600">{generatedResume.personal_info?.email}</p>
                      <p className="text-sm text-gray-600">{generatedResume.personal_info?.phone}</p>
                      
                      {includeSummary && generatedResume.summary && (
                        <div className="mt-4">
                          <h4 className="font-semibold text-sm uppercase text-gray-700 mb-2">Professional Summary</h4>
                          <p className="text-sm">{generatedResume.summary}</p>
                        </div>
                      )}
                      
                      {generatedResume.experience && generatedResume.experience.length > 0 && (
                        <div className="mt-4">
                          <h4 className="font-semibold text-sm uppercase text-gray-700 mb-2">Experience</h4>
                          {generatedResume.experience.map((exp: any, idx: number) => (
                            <div key={idx} className="mb-3">
                              <p className="font-semibold text-sm">{exp.title} - {exp.company}</p>
                              <p className="text-xs text-gray-600">{exp.start_date} - {exp.end_date}</p>
                              <ul className="list-disc list-inside text-xs mt-1">
                                {exp.description?.slice(0, 3).map((desc: string, i: number) => (
                                  <li key={i} className="text-gray-700">{desc.substring(0, 100)}...</li>
                                ))}
                              </ul>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {includeProjects && generatedResume.projects && generatedResume.projects.length > 0 && (
                        <div className="mt-4">
                          <h4 className="font-semibold text-sm uppercase text-gray-700 mb-2">Projects</h4>
                          {generatedResume.projects.map((project: any, idx: number) => (
                            <div key={idx} className="mb-3">
                              <p className="font-semibold text-sm">{project.name}</p>
                              <p className="text-xs text-gray-700">{project.description?.substring(0, 150)}...</p>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      <p className="text-xs text-gray-500 mt-4 italic">
                        This is a preview. Download the DOCX file for the full formatted resume.
                      </p>
                    </div>
                  </div>
                  
                  {/* Download Button at Bottom */}
                  <button
                    onClick={handleExportDocx}
                    className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold flex items-center justify-center space-x-2 transition-colors shadow-sm"
                  >
                    <Download className="h-5 w-5" />
                    <span>Download as DOCX</span>
                  </button>
                </div>
              ) : (
                <div className="text-center py-20">
                  {generating ? (
                    <div className="flex flex-col items-center space-y-4">
                      <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                      <p className="text-gray-600">AI is analyzing the job description and tailoring your resume...</p>
                    </div>
                  ) : (
                    <p className="text-gray-500">Paste a job description and click Generate to see your tailored resume here</p>
                  )}
                </div>
              )}
            </div>
          </div>
          </>
        )}
      </main>
      </div>

      {/* Contact Modal */}
      {showContactModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <Mail className="h-5 w-5 text-blue-600" />
                </div>
                <h2 className="text-xl font-semibold">Contact us</h2>
              </div>
              <button
                onClick={() => {
                  setShowContactModal(false);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleContactSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  placeholder="Your name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={contactEmail}
                  onChange={(e) => setContactEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                <textarea
                  value={contactMessage}
                  onChange={(e) => setContactMessage(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm min-h-[120px] resize-none"
                  placeholder="How can we help?"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowContactModal(false);
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                >
                  <Mail className="h-4 w-4" />
                  <span>Send message</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="max-w-6xl mx-auto px-6 py-4 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-500 space-y-2 sm:space-y-0">
          <div>
            {"\u00a9 2025 Ojogbon"}
          </div>
          <div className="text-center sm:text-left">
            {"AI-generated content \u2014 please review before use."}
          </div>
          <button
            type="button"
            onClick={() => setShowContactModal(true)}
            className="inline-flex items-center px-3 py-1.5 rounded-lg border text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 border-gray-300"
          >
            <Mail className="h-3 w-3 mr-1.5" />
            <span>Contact us</span>
          </button>
        </div>
      </footer>
    </div>
  );
}
