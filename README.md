# 🛡️ Aegis AI Pro

**A strategic AI co-pilot for content creators to ensure video compliance *before* publication.**

This project was developed for the AI Demos x VideoDB Hackathon (July 2025).

---

## 🚀 About the Project

Aegis AI Pro solves a critical business problem for content creators and brands: the risk of financial loss and channel penalties from accidentally violating the complex and ever-changing compliance guidelines of social media platforms.

Instead of a simple "checker," Aegis AI acts as a professional AI co-pilot. It uses a sophisticated Video RAG (Retrieval-Augmented Generation) pipeline to analyze a video's transcript against platform-specific rulebooks, providing a detailed, evidence-based compliance report and actionable strategic advice.

&nbsp;

## ✨ Features

• **Multi-Platform Analysis:** Audit videos against the specific guidelines for YouTube, Instagram, TikTok, and more.

• **Context-Aware AI:** The AI understands high-risk topics (like gambling or finance) and adjusts its analysis accordingly.

• **Evidence-Based Reporting:** Every identified risk is backed by a direct quote from the video's transcript.

• **Strategic Advisory:** Provides actionable advice on pre-publication edits, content risks, and post-publication strategy.


&nbsp;

## 🛠️ Tech Stack

• **Frontend:** Streamlit  
• **Video-to-Text:** VideoDB API  
• **AI Reasoning Engine:** OpenAI API (GPT-4o)  
• **Core Language:** Python

---

## ⚙️ Setup & Installation

To run this project locally, please follow these steps:

**1. Clone the repository:**
```bash
git clone https://github.com/Megesh07/Aegis-AI-Pro.git
cd Aegis-AI-Pro
```

**2. Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

**3. Install the required libraries:**
```bash
pip install -r requirements.txt
```

**4. Add API Keys:**
- Open the `app.py` file
- Paste your `VIDEODB_API_KEY` and `OPENAI_API_KEY` into the configuration section at the top of the file

&nbsp;

## ▶️ How to Run

Once the setup is complete, run the following command in your terminal:

```bash
streamlit run app.py
```

The application will open in your web browser.

---

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .gitignore             # Files to exclude from Git
├── README.md              # Project documentation
└── rules/                 # AI's knowledge base
    ├── facebook.txt
    ├── instagram.txt
    ├── linkedin.txt
    ├── tiktok.txt
    ├── x_twitter.txt
    └── youtube.txt
```

&nbsp;

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

&nbsp;

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

&nbsp;

## 🙏 Acknowledgments

• AI Demos x VideoDB Hackathon organizers  
• VideoDB for their powerful video processing API  
• OpenAI for GPT-4o capabilities
