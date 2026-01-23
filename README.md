# Cleaner Wannabe

**Cleaner Wannabe** is a modern, user-friendly system optimization tool for Windows. It helps you reclaim disk space, manage startup programs, and keep your system running smoothly with a "Comfy & Trusty" interface.

![Cleaner Wannabe Screenshot](https://via.placeholder.com/800x500?text=Cleaner+Wannabe+UI+Placeholder)
*(Replace with actual screenshot)*

## ✨ Features

-   **🧹 Smart System Cleaner**: Safely clean temporary files, prefetch data, browser caches (Chrome & Edge), and Recycle Bin.
-   **🔍 Large File Finder**: Visualize and manage large files cluttering your drives. Features a "Safe Delete" (Send to Recycle Bin) option.
-   **🚀 Startup Manager**: View and disable programs that slow down your Windows boot time.
-   **👯 Duplicate File Finder**: Scan specific folders (like Pictures) for identical files to save space.
-   **🗑️ Bulk Uninstaller**: Easily identify and uninstall unwanted applications.
-   **📊 System Monitor**: Real-time dashboard showing CPU and RAM usage, along with system health status.
-   **🛡️ Built for Safety**:
    -   **Safe Mode**: Deletions go to the Recycle Bin by default.
    -   **System Restore**: Option to create a restore point before major cleaning operations.
    -   **Admin Checks**: Visual indicators for Admin vs. User mode.

## 🛠️ Technology Stack

-   **Python 3.12+**
-   **GUI**: `customtkinter` (Modern, dark-mode ready UI)
-   **System Interaction**: `psutil`, `ctypes`, `winshell`, `winreg`
-   **Safety**: `send2trash`

## 🚀 Getting Started

### Prerequisites

-   Python 3.10 or higher
-   Windows 10/11

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/aeoncyr/cleaner-wannabe.git
    cd cleaner-wannabe
    ```

2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You may need to create a requirements.txt file if one doesn't exist, containing: `customtkinter`, `psutil`, `send2trash`, `darkdetect`, `pillow`, `winshell`)*

### Usage

Run the main application:
```bash
python main.py
```
*(Run as Administrator for full cleaning capabilities)*

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).

---
*Developed with ❤️ by Advan Workplus*
