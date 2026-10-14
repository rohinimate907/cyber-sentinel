#!/bin/bash

# PentestX Professional Installation Script
# Automated installation with comprehensive error handling and system checks
# Version: 2.0

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Installation configuration
PYTHON_MIN_VERSION="3.10"
VENV_NAME="pentestx-env"
INSTALL_LOG="pentestx_install.log"

# Function to print colored output with timestamps
print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] [INFO]${NC} $1" | tee -a "$INSTALL_LOG"
}

print_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] [SUCCESS]${NC} $1" | tee -a "$INSTALL_LOG"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] [WARNING]${NC} $1" | tee -a "$INSTALL_LOG"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] [ERROR]${NC} $1" | tee -a "$INSTALL_LOG"
}

print_header() {
    echo -e "${CYAN}${BOLD}$1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Enhanced Python version check
check_python_version() {
    local python_cmd=""
    
    # Try different Python commands
    for cmd in python3 python python3.10 python3.11 python3.12; do
        if command_exists "$cmd"; then
            local version=$($cmd -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>/dev/null || echo "0.0")
            local major=$(echo "$version" | cut -d. -f1)
            local minor=$(echo "$version" | cut -d. -f2)
            
            if [[ $major -ge 3 && $minor -ge 10 ]]; then
                python_cmd="$cmd"
                print_success "Found Python $version at $(which $cmd)"
                echo "$python_cmd"
                return 0
            fi
        fi
    done
    
    return 1
}

# Function to detect OS and package manager
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            echo "ubuntu"
        elif command_exists yum; then
            echo "centos"
        elif command_exists pacman; then
            echo "arch"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to install Python on different systems
install_python() {
    local os=$(detect_os)
    print_status "Attempting to install Python 3.10+ on $os system..."
    
    case "$os" in
        "ubuntu")
            print_status "Installing Python via apt..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv python3-dev
            ;;
        "centos")
            print_status "Installing Python via yum..."
            sudo yum install -y python3 python3-pip python3-venv python3-devel
            ;;
        "macos")
            if command_exists brew; then
                print_status "Installing Python via Homebrew..."
                brew install python@3.10
            else
                print_error "Homebrew not found. Please install Python manually from https://python.org"
                return 1
            fi
            ;;
        *)
            print_error "Unsupported OS. Please install Python 3.10+ manually"
            return 1
            ;;
    esac
}

# Function to create environment file
create_env_file() {
    if [[ ! -f ".env" ]]; then
        print_status "Creating environment configuration file..."
        cat > .env << 'EOF'
# PentestX Configuration File
# Edit this file with your specific settings

# ===========================================
# NETLAS API CONFIGURATION (REQUIRED)
# ===========================================
# Get your API key from: https://netlas.io/
NETLAS_API_KEY=your_netlas_api_key_here

# ===========================================
# RATE LIMITING & PERFORMANCE
# ===========================================
RATE_LIMIT=10
MAX_RETRIES=3
TIMEOUT=30
BACKOFF_FACTOR=2.0

# ===========================================
# OUTPUT CONFIGURATION
# ===========================================
OUTPUT_DIR=./output
DEFAULT_FORMAT=json

# ===========================================
# OPTIONAL TOOLS (Auto-detected)
# ===========================================
SUBFINDER_PATH=subfinder
AMASS_PATH=amass

# ===========================================
# LOGGING
# ===========================================
LOG_LEVEL=INFO
LOG_FILE=pentestx.log
EOF
        print_success "Configuration file created (.env)"
        print_warning "⚠️  IMPORTANT: Edit .env file with your Netlas API key before using PentestX"
    else
        print_warning "Configuration file already exists"
    fi
}

# Function to verify installation
verify_installation() {
    print_status "Verifying PentestX installation..."
    
    # Test package import
    if "$PYTHON_CMD" -c "import pentestx; print(f'PentestX v{pentestx.__version__} imported successfully')" 2>/dev/null; then
        print_success "Package import verification passed"
    else
        print_error "Package import failed"
        return 1
    fi
    
    # Test CLI access
    if "$PYTHON_CMD" -m pentestx --version >/dev/null 2>&1; then
        local version=$("$PYTHON_CMD" -m pentestx --version 2>/dev/null || echo "Unknown")
        print_success "CLI verification passed: $version"
    else
        print_warning "CLI command not directly accessible, but package is installed"
        print_status "You can still run: python -m pentestx"
    fi
    
    return 0
}

# Function to check and install optional tools
setup_optional_tools() {
    print_header "🔧 Checking Optional Tools"
    
    local tools_found=0
    
    # Check Go installation for tools
    if ! command_exists go; then
        print_warning "Go not found - some optional tools may not be installable"
        print_status "Install Go from: https://golang.org/dl/"
    fi
    
    # Check subfinder
    if command_exists subfinder; then
        local sf_version=$(subfinder -version 2>/dev/null | head -n1 || echo "Unknown version")
        print_success "Subfinder found: $sf_version"
        ((tools_found++))
    else
        print_warning "Subfinder not found (optional subdomain enumeration tool)"
        if command_exists go; then
            print_status "Install with: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
        fi
    fi
    
    # Check amass
    if command_exists amass; then
        local amass_version=$(amass -version 2>/dev/null | head -n1 || echo "Unknown version")
        print_success "Amass found: $amass_version"
        ((tools_found++))
    else
        print_warning "Amass not found (optional network mapping tool)"
        if command_exists go; then
            print_status "Install with: go install -v github.com/OWASP/Amass/v3/...@master"
        fi
    fi
    
    if [[ $tools_found -eq 0 ]]; then
        print_warning "No optional tools found - PentestX will work with Netlas API only"
    else
        print_success "Found $tools_found optional tool(s)"
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up temporary files..."
    [[ -f "$INSTALL_LOG.tmp" ]] && rm -f "$INSTALL_LOG.tmp"
}

# Trap cleanup on exit
trap cleanup EXIT

# Main installation function
main() {
    # Initialize log
    echo "PentestX Installation Started: $(date)" > "$INSTALL_LOG"
    
    print_header "🎯 PentestX Professional Installation"
    print_status "Installation log: $INSTALL_LOG"
    
    # Check prerequisites
    print_header "📋 Checking Prerequisites"
    
    # Check Python
    PYTHON_CMD=$(check_python_version)
    if [[ $? -ne 0 ]]; then
        print_error "Python 3.10 or higher is required"
        print_status "Current Python installations:"
        for cmd in python python3 python3.10 python3.11 python3.12; do
            if command_exists "$cmd"; then
                local ver=$($cmd --version 2>&1 || echo "Error getting version")
                print_status "  $cmd: $ver"
            fi
        done
        
        print_status "Would you like to attempt automatic Python installation? (y/N)"
        read -r install_python
        if [[ "$install_python" =~ ^[Yy]$ ]]; then
            install_python || {
                print_error "Python installation failed"
                print_status "Please install Python 3.10+ manually from: https://python.org/downloads/"
                exit 1
            }
            PYTHON_CMD=$(check_python_version) || {
                print_error "Python installation verification failed"
                exit 1
            }
        else
            print_status "Please install Python 3.10+ manually from: https://python.org/downloads/"
            exit 1
        fi
    fi
    
    # Check Git
    if ! command_exists git; then
        print_error "Git is required but not installed"
        print_status "Please install Git from: https://git-scm.com/downloads"
        exit 1
    fi
    print_success "Git check passed"
    
    # Check pip
    if ! "$PYTHON_CMD" -m pip --version >/dev/null 2>&1; then
        print_error "pip is required but not available"
        print_status "Please ensure pip is installed with your Python installation"
        exit 1
    fi
    print_success "pip check passed"
    
    # Create and activate virtual environment
    print_header "🔨 Setting Up Environment"
    
    if [[ ! -d "$VENV_NAME" ]]; then
        print_status "Creating virtual environment: $VENV_NAME"
        "$PYTHON_CMD" -m venv "$VENV_NAME" || {
            print_error "Failed to create virtual environment"
            exit 1
        }
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source "$VENV_NAME/bin/activate" || {
        print_error "Failed to activate virtual environment"
        exit 1
    }
    
    # Upgrade pip in venv
    print_status "Upgrading pip in virtual environment..."
    python -m pip install --upgrade pip setuptools wheel || {
        print_error "Failed to upgrade pip"
        exit 1
    }
    
    # Install dependencies
    print_header "📦 Installing Dependencies"
    
    print_status "Installing PentestX dependencies..."
    if [[ -f "requirements.txt" ]]; then
        python -m pip install -r requirements.txt || {
            print_error "Failed to install requirements.txt"
            exit 1
        }
    elif [[ -f "requirements/requirements.txt" ]]; then
        python -m pip install -r requirements/requirements.txt || {
            print_error "Failed to install requirements/requirements.txt"
            exit 1
        }
    else
        print_warning "No requirements file found, installing from pyproject.toml"
    fi
    
    # Install PentestX package
    print_status "Installing PentestX package..."
    python -m pip install -e . || {
        print_error "Failed to install PentestX package"
        exit 1
    }
    print_success "PentestX package installed"
    
    # Setup configuration
    print_header "⚙️ Configuration Setup"
    create_env_file
    
    # Create output directory
    if [[ ! -d "output" ]]; then
        mkdir -p output
        print_success "Output directory created"
    fi
    
    # Setup optional tools
    setup_optional_tools
    
    # Verify installation
    print_header "✅ Installation Verification"
    verify_installation || {
        print_error "Installation verification failed"
        exit 1
    }
    
    # Installation complete
    print_header "🎉 Installation Complete!"
    
    echo
    print_success "PentestX has been successfully installed!"
    echo
    print_status "📝 Next Steps:"
    echo
    echo "  1. Configure your Netlas API key:"
    echo "     nano .env"
    echo "     # Add your API key: NETLAS_API_KEY=your_actual_key_here"
    echo
    echo "  2. Activate the environment and test installation:"
    echo "     source $VENV_NAME/bin/activate"
    echo "     python -m pentestx --version"
    echo
    echo "  3. Launch interactive mode:"
    echo "     python -m pentestx menu"
    echo
    echo "  4. Or run a quick scan:"
    echo "     python -m pentestx scan example.com"
    echo
    print_status "🔧 Optional Improvements:"
    echo "  - Install subfinder: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    echo "  - Install amass: go install -v github.com/OWASP/Amass/v3/...@master"
    echo
    print_status "📚 Documentation:"
    echo "  - README.md - Usage guide and examples"
    echo "  - .env - Configuration file (edit with your API key)"
    echo "  - $INSTALL_LOG - Installation log"
    echo
    print_status "🆘 Support:"
    echo "  - GitHub: https://github.com/pentestx/pentestx"
    echo "  - Issues: Report problems via GitHub Issues"
    echo
    print_success "Happy reconnaissance! 🎯"
}

# Check if running from correct directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -f "src/pentestx/__init__.py" ]]; then
    print_error "Please run this script from the PentestX project root directory"
    print_status "Current directory: $(pwd)"
    print_status "Expected files: pyproject.toml, src/pentestx/__init__.py"
    exit 1
fi

# Run main installation
main "$@"
