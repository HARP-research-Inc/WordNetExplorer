"""
WordNet Data Access Module

Handles downloading and accessing WordNet data through NLTK.
"""

import nltk
import os


def download_nltk_data(quiet=False):
    """Download required NLTK data if not already present."""
    required_data = [
        ('corpora/wordnet', 'wordnet'),
        ('corpora/omw-1.4', 'omw-1.4')
    ]
    
    for data_path, download_name in required_data:
        try:
            nltk.data.find(data_path)
            if not quiet:
                print(f"✓ {download_name} already available")
        except LookupError:
            if not quiet:
                print(f"Downloading {download_name} data...")
            try:
                nltk.download(download_name, quiet=quiet)
                if not quiet:
                    print(f"✓ {download_name} downloaded successfully")
            except Exception as e:
                print(f"Warning: Failed to download {download_name}: {e}")
                # Try alternative download location
                try:
                    nltk.download(download_name, download_dir=os.path.expanduser('~/nltk_data'), quiet=quiet)
                    if not quiet:
                        print(f"✓ {download_name} downloaded to alternative location")
                except Exception as e2:
                    print(f"Error: Could not download {download_name}: {e2}")
                    raise


def verify_wordnet_access():
    """Verify that WordNet can be accessed properly."""
    try:
        from nltk.corpus import wordnet as wn
        # Try a simple operation to ensure it works
        test_synsets = wn.synsets('test')
        return True
    except Exception as e:
        print(f"WordNet access verification failed: {e}")
        return False


def initialize_wordnet():
    """Initialize WordNet with proper error handling."""
    try:
        # First, ensure data is downloaded
        download_nltk_data(quiet=True)
        
        # Then verify access
        if verify_wordnet_access():
            return True
        else:
            # If verification fails, try re-downloading
            print("Re-downloading WordNet data...")
            download_nltk_data(quiet=False)
            return verify_wordnet_access()
    except Exception as e:
        print(f"Failed to initialize WordNet: {e}")
        return False 