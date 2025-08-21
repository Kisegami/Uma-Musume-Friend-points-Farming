#!/usr/bin/env python3
"""
Uma Friend Point Farm Automation Script
Uses ADB for screen capture and control with template matching
"""

import json
import time
import cv2
import numpy as np
import subprocess
import os
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UmaAutomation:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the automation with configuration"""
        self.config = self.load_config(config_path)
        self.device_address = self.config["adb"]["device_address"]
        self.template_path = self.config["adb"]["template_path"]
        self.screenshot_path = self.config["adb"]["screenshot_path"]
        
        # Create directories if they don't exist
        os.makedirs(self.screenshot_path, exist_ok=True)
        
        # Test ADB connection
        self.test_adb_connection()
        
    def load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_path} not found!")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file {config_path}")
            raise
    
    def test_adb_connection(self):
        """Test ADB connection to device"""
        try:
            result = subprocess.run(
                ["adb", "connect", self.device_address],
                capture_output=True,
                text=True,
                timeout=10
            )
            if "connected" in result.stdout.lower():
                logger.info(f"Successfully connected to {self.device_address}")
            else:
                logger.warning(f"ADB connection result: {result.stdout}")
        except subprocess.TimeoutExpired:
            logger.error("ADB connection timeout")
            raise
        except FileNotFoundError:
            logger.error("ADB not found. Please install Android SDK and add to PATH")
            raise
    
    def take_screenshot(self) -> str:
        """Take a screenshot and return the file path"""
        timestamp = int(time.time())
        filename = f"{self.screenshot_path}/screenshot_{timestamp}.png"
        
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_address, "exec-out", "screencap -p"],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                with open(filename, 'wb') as f:
                    f.write(result.stdout)
                logger.info(f"Screenshot saved: {filename}")
                return filename
            else:
                logger.error(f"Screenshot failed: {result.stderr}")
                raise RuntimeError("Failed to take screenshot")
                
        except subprocess.TimeoutExpired:
            logger.error("Screenshot timeout")
            raise
    
    def find_template(self, template_name: str, screenshot_path: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """Find template image on screenshot using template matching"""
        template_file = os.path.join(self.template_path, template_name)
        
        if not os.path.exists(template_file):
            logger.error(f"Template file not found: {template_file}")
            return None
        
        try:
            # Read images
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_file)
            
            if screenshot is None or template is None:
                logger.error("Failed to read image files")
                return None
            
            # Convert to grayscale for better matching
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # Calculate center of template
                h, w = template_gray.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                logger.info(f"Found {template_name} at ({center_x}, {center_y}) with confidence {max_val:.3f}")
                return (center_x, center_y)
            else:
                logger.debug(f"Template {template_name} not found (confidence: {max_val:.3f})")
                return None
                
        except Exception as e:
            logger.error(f"Error in template matching: {e}")
            return None
    
    def tap_coordinate(self, x: int, y: int):
        """Tap at specific coordinates"""
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_address, "shell", "input", "tap", str(x), str(y)],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Tapped at ({x}, {y})")
            else:
                logger.error(f"Tap failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Tap command timeout")
    
    def wait(self, seconds: int):
        """Wait for specified seconds"""
        logger.info(f"Waiting {seconds} seconds...")
        time.sleep(seconds)
    
    def find_and_tap(self, template_name: str, max_attempts: int = 10, wait_after: int = 0) -> bool:
        """Find template and tap it with retry logic"""
        for attempt in range(max_attempts):
            screenshot_path = self.take_screenshot()
            
            try:
                coords = self.find_template(template_name, screenshot_path)
                if coords:
                    self.tap_coordinate(coords[0], coords[1])
                    if wait_after > 0:
                        self.wait(wait_after)
                    return True
                else:
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts}: {template_name} not found")
                    if attempt < max_attempts - 1:
                        self.wait(1)  # Brief wait between attempts
                        
            finally:
                # Clean up screenshot
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
        
        logger.error(f"Failed to find and tap {template_name} after {max_attempts} attempts")
        return False

    def find_template_multi(self, template_name: str, screenshot_path: str, threshold: float = 0.8, extra_dirs: Optional[list] = None) -> Optional[Tuple[int, int]]:
        """Find template by checking primary template path and optional extra directories"""
        if extra_dirs is None:
            extra_dirs = [os.path.join("assets", "image")]
        # First try primary buttons directory
        coords = self.find_template(template_name, screenshot_path, threshold)
        if coords:
            return coords
        # Then try each extra directory
        for directory in extra_dirs:
            template_file = os.path.join(directory, template_name)
            if not os.path.exists(template_file):
                continue
            try:
                screenshot = cv2.imread(screenshot_path)
                template = cv2.imread(template_file)
                if screenshot is None or template is None:
                    continue
                screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val >= threshold:
                    h, w = template_gray.shape
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    logger.info(f"Found {template_name} in {directory} at ({center_x}, {center_y}) with confidence {max_val:.3f}")
                    return (center_x, center_y)
            except Exception as e:
                logger.error(f"Error searching {template_name} in {directory}: {e}")
        return None

    def find_and_tap_multi(self, template_name: str, max_attempts: int = 10, wait_after: float = 0.0, extra_dirs: Optional[list] = None, threshold: float = 0.8) -> bool:
        """Find and tap a template by searching multiple directories with a configurable threshold"""
        for attempt in range(max_attempts):
            screenshot_path = self.take_screenshot()
            try:
                coords = self.find_template_multi(template_name, screenshot_path, threshold, extra_dirs)
                if coords:
                    self.tap_coordinate(coords[0], coords[1])
                    if wait_after > 0:
                        time.sleep(wait_after)
                    return True
                else:
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts}: {template_name} not found (multi)")
                    if attempt < max_attempts - 1:
                        time.sleep(1)
            finally:
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
        logger.error(f"Failed to find and tap {template_name} (multi) after {max_attempts} attempts")
        return False

    def run_filter_sequence(self) -> bool:
        """Execute the filter sequence to locate Following list based on config preferences"""
        logger.info("Starting filter sequence")
        # 3.1 Tap Filter button
        self.tap_coordinate(747, 1623)
        time.sleep(0.5)
        # 3.2 Tap to open sorting/filter options
        self.tap_coordinate(786, 203)
        time.sleep(0.5)
        # 3.3 Tap on Rarity and Speciality based on config
        filter_config = self.config.get("automation", {}).get("filter", {})
        rarity_choice = str(filter_config.get("rarity", "SSR")).upper()
        speciality_choice = str(filter_config.get("speciality", "POWER")).upper()
        rarity_coords = {
            "R": (102, 408),
            "SR": (437, 414),
            "SSR": (777, 410),
        }
        speciality_coords = {
            "SPEED": (102, 627),
            "STAMINA": (444, 623),
            "POWER": (786, 618),
            "GUTS": (109, 741),
            "WIT": (442, 732),
            "PAL": (777, 731),
        }
        if rarity_choice not in rarity_coords:
            logger.error(f"Unknown rarity selection: {rarity_choice}")
            return False
        if speciality_choice not in speciality_coords:
            logger.error(f"Unknown speciality selection: {speciality_choice}")
            return False
        self.tap_coordinate(*rarity_coords[rarity_choice])
        time.sleep(0.2)
        self.tap_coordinate(*speciality_coords[speciality_choice])
        time.sleep(0.2)
        # 3.4 Tap OK
        if not self.find_and_tap("ok.png", 10):
            logger.error("Failed to confirm filter (OK not found)")
            return False
        time.sleep(0.5)
        logger.info("Filter sequence completed")
        return True

    def manual_choose_friend(self) -> bool:
        """Manually choose a friend using plus and following with optional filter sequence"""
        logger.info("Starting manual choose friend sequence")
        # 1. Find and tap plus.png, wait 1s
        if not self.find_and_tap_multi("plus.png", max_attempts=10, wait_after=1.0):
            logger.error("Failed to find plus.png for manual choose")
            return False
        # 2. Try to find following.png (5 attempts) and tap (use 0.7 threshold)
        if self.find_and_tap_multi("following.png", max_attempts=5, wait_after=0.2, threshold=0.7):
            logger.info("Found following.png and tapped successfully")
            return True
        # 3. If cannot find, run filter sequence
        logger.info("following.png not found, running filter sequence")
        if not self.run_filter_sequence():
            logger.error("Filter sequence failed")
            return False
        # 4. After filter, try again with 0.7 threshold; if still not found, stop
        if self.find_and_tap_multi("following.png", max_attempts=5, wait_after=0.2, threshold=0.7):
            logger.info("Found following.png after filter and tapped successfully")
            return True
        else:
            logger.error("following.png not found after filter; stopping automation")
            return False
    
    def find_use_buttons_with_brightness_filter(self, screenshot_path: str, brightness_threshold: int = 170) -> list:
        """Find all use.png buttons and filter by brightness, returning unique coordinates"""
        template_file = os.path.join(self.template_path, "use.png")
        
        if not os.path.exists(template_file):
            logger.error("Template file use.png not found")
            return []
        
        try:
            # Read images
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_file)
            
            if screenshot is None or template is None:
                logger.error("Failed to read image files")
                return []
            
            # Convert to grayscale for template matching
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            
            # Find all matches above threshold
            threshold = 0.8
            locations = np.where(result >= threshold)
            matches = list(zip(*locations[::-1]))  # Convert to (x, y) format
            
            # Filter by brightness and get unique coordinates
            unique_coords = []
            h, w = template_gray.shape
            
            for match in matches:
                x, y = match
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Check brightness at center of template
                if center_y < screenshot_gray.shape[0] and center_x < screenshot_gray.shape[1]:
                    brightness = screenshot_gray[center_y, center_x]
                    
                    if brightness > brightness_threshold:
                        # Check if this coordinate is far enough from existing ones
                        is_unique = True
                        for existing_coord in unique_coords:
                            distance = np.sqrt((center_x - existing_coord[0])**2 + (center_y - existing_coord[1])**2)
                            if distance < 50:  # Minimum distance threshold
                                is_unique = False
                                break
                        
                        if is_unique:
                            unique_coords.append((center_x, center_y))
            
            logger.info(f"Found {len(unique_coords)} unique use buttons with brightness > {brightness_threshold}")
            return unique_coords
            
        except Exception as e:
            logger.error(f"Error in finding use buttons with brightness filter: {e}")
            return []
    
    def tp_charge(self) -> bool:
        """TP Charge function - handles the charging process"""
        logger.info("Starting TP Charge process...")
        
        try:
            # Step 1: Find and tap restore.png
            logger.info("TP Charge Step 1: Finding and tapping restore.png")
            if not self.find_and_tap("restore.png", 10):
                logger.error("Failed to find restore.png in TP Charge")
                return False
            self.wait(0.5)
            
            # Step 2: Find use.png buttons with brightness filter and de-duplication
            logger.info("TP Charge Step 2: Finding use.png buttons with brightness filter")
            screenshot_path = self.take_screenshot()
            try:
                use_coords = self.find_use_buttons_with_brightness_filter(screenshot_path, 170)
                if not use_coords:
                    logger.error("No use.png buttons found with brightness filter")
                    return False
                
                # Step 3: Tap first use.png button
                logger.info("TP Charge Step 3: Tapping first use.png button")
                first_use_coord = use_coords[0]
                self.tap_coordinate(first_use_coord[0], first_use_coord[1])
                
            finally:
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
            self.wait(0.5)
            
            # Step 4: Find and tap max.png
            logger.info("TP Charge Step 4: Finding and tapping max.png")
            if not self.find_and_tap("max.png", 10):
                logger.error("Failed to find max.png in TP Charge")
                return False
            
            # Step 5: Find and tap ok.png
            logger.info("TP Charge Step 5: Finding and tapping ok.png")
            if not self.find_and_tap("ok.png", 10):
                logger.error("Failed to find ok.png in TP Charge")
                return False
            self.wait(1.5)

            # Step 6: Find and tap close.png
            logger.info("TP Charge Step 6: Finding and tapping close.png")
            if not self.find_and_tap("close.png", 20):
                logger.error("Failed to find close.png in TP Charge")
                return False
            self.wait(0.5)
            
            logger.info("TP Charge process completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in TP Charge process: {e}")
            return False
    
    def run_automation_loop(self):
        """Main automation loop"""
        logger.info("Starting Uma automation loop...")
        
        while True:
            try:
                logger.info("=== Starting new automation cycle ===")
                
                # Step 1: Find and Tap on Career.png
                logger.info("Step 1: Finding and tapping Career button")
                if not self.find_and_tap("Career.png", 10):
                    logger.error("Failed to find Career button, retrying...")
                    continue
                
                # Step 2: Wait 10s
                logger.info("Step 2: Waiting 10 seconds")
                self.wait(self.config["automation"]["wait_time"]["career"])
                
                # Step 3: Find next.png (10 attempts) and tap it, wait 1s. Do this again 1 time
                logger.info("Step 3: Finding and tapping Next button (first time)")
                if not self.find_and_tap("next.png", self.config["automation"]["attempts"]["next"], 
                                       self.config["automation"]["wait_time"]["next"]):
                    logger.error("Failed to find Next button (first time)")
                    continue
                self.wait(0.5)
                
                logger.info("Step 3: Finding and tapping Next button (second time)")
                if not self.find_and_tap("next.png", self.config["automation"]["attempts"]["next"], 
                                       self.config["automation"]["wait_time"]["next"]):
                    logger.error("Failed to find Next button (second time)")
                    continue
                self.wait(0.5)
                
                # Step 4: Find and press auto_select_1.png, find and tap ok
                logger.info("Step 4: Finding and tapping Auto-Select 1, then OK")
                if not self.find_and_tap("auto_select_1.png", 10):
                    logger.error("Failed to find Auto-Select 1 button")
                    continue
                self.wait(0.5)
                if not self.find_and_tap("ok.png", 10):
                    logger.error("Failed to find OK button after Auto-Select 1")
                    continue
                self.wait(0.5)
                if not self.find_and_tap("next.png", 10):
                    logger.error("Failed to find Next button after OK button")
                    continue
                self.wait(2)
                
                # Step 5: Manual choosing is optional; default is automatic by the game
                manual_choose_enabled = self.config.get("automation", {}).get("manual_choose", False)
                if manual_choose_enabled:
                    logger.info("Step 5: Manual choose enabled - running manual selection sequence")
                    if not self.manual_choose_friend():
                        logger.error("Manual choose failed; stopping automation as requested")
                        break
                else:
                    logger.info("Step 5: Skipping - selection handled automatically by the game")
                
                # Step 6: Find and tap start_career_1.png and handle TP Charge if needed
                logger.info("Step 6: Finding and tapping Start Career 1")
                
                # Local loop for Steps 6-6.5 until no TP Charge is needed
                while True:
                    if not self.find_and_tap("start_career_1.png", 10):
                        logger.error("Failed to find Start Career 1 button")
                        break  # Exit local loop and continue to next step
                    
                    self.wait(0.5)
                    
                    # Step 6.5: Check for restore.png and do TP Charge if found
                    logger.info("Step 6.5: Checking for restore.png to trigger TP Charge")
                    screenshot_path = self.take_screenshot()
                    try:
                        coords = self.find_template("restore.png", screenshot_path)
                        if coords:
                            logger.info("Found restore.png, starting TP Charge process")
                            if self.tp_charge():
                                logger.info("TP Charge completed successfully, retrying Step 6")
                                # Continue the local loop to retry start_career_1.png
                                continue
                            else:
                                logger.warning("TP Charge failed, continuing with automation")
                                break  # Exit local loop and continue to next step
                        else:
                            logger.info("No restore.png found, continuing with automation")
                            break  # Exit local loop and continue to next step
                    finally:
                        if os.path.exists(screenshot_path):
                            os.remove(screenshot_path)
                
                # If we broke out of the local loop due to failure, restart main cycle
                if not self.find_and_tap("start_career_1.png", 1):  # Quick check if we're still on the right screen
                    logger.error("Failed to complete Step 6, restarting main cycle")
                    continue
                
                # Step 7: Find and tap start_career_2.png
                logger.info("Step 7: Finding and tapping Start Career 2")
                if not self.find_and_tap("start_career_2.png", 10):
                    logger.error("Failed to find Start Career 2 button")
                    continue
                
                # Step 8: Wait 2s
                logger.info("Step 8: Waiting 2 seconds")
                self.wait(self.config["automation"]["wait_time"]["start_career"])
                
                # Step 9: Find and tap skip.png
                logger.info("Step 9: Finding and tapping Skip button")
                if not self.find_and_tap("skip.png", 10):
                    logger.error("Failed to find Skip button")
                    continue
                self.wait(0.5)
                
                # Step 10: Find and tap skip_btn.png
                logger.info("Step 10: Finding and tapping Skip Button")
                if not self.find_and_tap("skip_btn.png", 10):
                    logger.error("Failed to find Skip Button")
                    continue
                
                # Step 11: Wait 1s and Tap coordinate (249,948)
                logger.info("Step 11: Waiting 1 second and tapping coordinate")
                self.wait(self.config["automation"]["wait_time"]["skip"])
                coords = self.config["automation"]["coordinates"]["tap_after_skip"]
                self.tap_coordinate(coords[0], coords[1])
                
                # Step 12: Find skip_off.png and double tap, then check for different states
                logger.info("Step 12: Finding skip_off.png and double tapping, then checking for different states")
                screenshot_path = self.take_screenshot()
                try:
                    coords = self.find_template("skip_off.png", screenshot_path)
                    if coords:
                        # Double tap
                        self.tap_coordinate(coords[0], coords[1])
                        time.sleep(0.2)
                        self.tap_coordinate(coords[0], coords[1])
                        logger.info("Double tapped skip_off.png")
                        
                        # Wait 0.2s and check for different states
                        time.sleep(0.2)
                        screenshot_path_check = self.take_screenshot()
                        try:
                            # Check for skip_off.png again
                            coords_off = self.find_template("skip_off.png", screenshot_path_check)
                            if coords_off:
                                logger.info("Found skip_off.png again, double tapping again")
                                self.tap_coordinate(coords_off[0], coords_off[1])
                                time.sleep(0.2)
                                self.tap_coordinate(coords_off[0], coords_off[1])
                            else:
                                # Check for skip_on_1.png
                                coords_on1 = self.find_template("skip_on_1.png", screenshot_path_check)
                                if coords_on1:
                                    logger.info("Found skip_on_1.png, single tapping")
                                    self.tap_coordinate(coords_on1[0], coords_on1[1])
                                else:
                                    # Check for skip_on_2.png
                                    coords_on2 = self.find_template("skip_on_2.png", screenshot_path_check)
                                    if coords_on2:
                                        logger.info("Found skip_on_2.png, continuing...")
                                    else:
                                        logger.info("No specific skip state found, continuing...")
                        finally:
                            if os.path.exists(screenshot_path_check):
                                os.remove(screenshot_path_check)
                    else:
                        logger.warning("skip_off.png not found, continuing...")
                finally:
                    if os.path.exists(screenshot_path):
                        os.remove(screenshot_path)
                
                # Step 13: Find and tap confirm.png
                logger.info("Step 12: Finding and tapping Confirm button")
                if not self.find_and_tap("confirm.png", 10):
                    logger.error("Failed to find Confirm button")
                    continue
                self.wait(1)
                
                # Step 14: Wait 5s
                logger.info("Step 14: Waiting 5 seconds")
                self.wait(self.config["automation"]["wait_time"]["confirm"])
                
                # Step 14.5: Check for If(1) happen or not
                logger.info("Step 14.5: Checking for additional Next button opportunities")
                screenshot_path = self.take_screenshot()
                try:
                    coords = self.find_template("next.png", screenshot_path)
                    if coords:
                        logger.info("Found additional Next button, tapping 5 times")
                        for i in range(5):
                            self.tap_coordinate(coords[0], coords[1])
                            time.sleep(0.5)
                    else:
                        logger.info("No additional Next button found, continuing...")
                finally:
                    if os.path.exists(screenshot_path):
                        os.remove(screenshot_path)
                
                # Step 15: Find and tap menu.png
                logger.info("Step 15: Finding and tapping Menu button")
                if not self.find_and_tap("menu.png", 10):
                    logger.error("Failed to find Menu button")
                    continue
                
                # Step 16: Find and tap give_up_1.png
                logger.info("Step 16: Finding and tapping Give Up 1")
                
                # Infinite loop between steps 14.5 and 16 until step 16 succeeds
                while True:
                    if not self.find_and_tap("give_up_1.png", 5):
                        logger.error("Failed to find Give Up 1 button, returning to step 14.5")
                        # Return to step 14.5: Check for additional Next button opportunities
                        logger.info("Returning to Step 14.5: Checking for additional Next button opportunities")
                        screenshot_path = self.take_screenshot()
                        try:
                            coords = self.find_template("next.png", screenshot_path)
                            if coords:
                                logger.info("Found additional Next button, tapping 5 times")
                                for i in range(5):
                                    self.tap_coordinate(coords[0], coords[1])
                                    time.sleep(0.5)
                            else:
                                logger.info("No additional Next button found, continuing...")
                        finally:
                            if os.path.exists(screenshot_path):
                                os.remove(screenshot_path)
                        
                        # After step 14.5, continue with step 15
                        logger.info("Continuing with Step 15 after step 14.5")
                        
                        # Step 15: Find and tap menu.png
                        logger.info("Step 15: Finding and tapping Menu button")
                        if not self.find_and_tap("menu.png", 10):
                            logger.error("Failed to find Menu button")
                            continue
                        
                        # Continue the loop to retry step 16
                        logger.info("Retrying Step 16 after step 15")
                        continue
                    else:
                        # Step 16 succeeded, break out of the infinite loop
                        logger.info("Step 16 succeeded, proceeding to Step 17")
                        break
                
                # Step 17: Find and tap give_up_2.png
                logger.info("Step 17: Finding and tapping Give Up 2")
                if not self.find_and_tap("give_up_2.png", 5):
                    logger.error("Failed to find Give Up 2 button")
                    continue
                
                # Step 18: Wait 5s and loop again
                logger.info("Step 18: Waiting 5 seconds before next cycle")
                self.wait(self.config["automation"]["wait_time"]["loop"])
                
                logger.info("=== Automation cycle completed successfully ===")
                
            except KeyboardInterrupt:
                logger.info("Automation stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in automation loop: {e}")
                logger.info("Waiting 10 seconds before retrying...")
                time.sleep(10)

def main():
    """Main function"""
    try:
        automation = UmaAutomation()
        automation.run_automation_loop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
