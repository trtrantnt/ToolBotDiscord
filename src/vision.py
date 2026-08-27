import cv2
import numpy as np
import pyautogui
import os

class VisionManager:
    def __init__(self, templates_dir="templates"):
        self.templates_dir = templates_dir
        self.templates = self._load_templates()

    def _load_templates(self):
        templates = {}
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            print(f"Created directory: {self.templates_dir}. Please add image templates here.")
            return templates

        for root, _, files in os.walk(self.templates_dir):
            for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    full_path = os.path.join(root, filename)
                    # Đường dẫn tương đối tính từ templates_dir
                    rel_path = os.path.relpath(full_path, self.templates_dir).replace('\\', '/')
                    
                    # Load image in grayscale
                    img = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        # Lưu cả tên file đơn lẻ và đường dẫn tương đối (ví dụ: 'sinh.png' và 'gates/sinh.png')
                        templates[filename] = img
                        templates[rel_path] = img
                        templates[rel_path.replace('/', '\\')] = img
                        print(f"Loaded template: {rel_path}")
                    else:
                        print(f"Failed to load template: {full_path}")
        return templates

    def reload_templates(self):
        self.templates = self._load_templates()

    def find_all_occurrences(self, template_name, threshold=0.8):
        """
        Takes a screenshot and looks for all occurrences of the specified template.
        Returns a list of (x, y, w, h) bounding boxes.
        """
        if template_name not in self.templates:
            print(f"Template {template_name} not found.")
            return []
            
        template_img = self.templates[template_name]
        h, w = template_img.shape
        
        screenshot = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        
        result = cv2.matchTemplate(screenshot_cv, template_img, cv2.TM_CCOEFF_NORMED)
        
        # Get all locations above threshold
        locations = np.where(result >= threshold)
        
        boxes = []
        for pt in zip(*locations[::-1]):  # Switch x and y
            boxes.append((pt[0], pt[1], w, h))
            
        # Group overlapping boxes to avoid counting the same icon multiple times
        grouped_boxes = cv2.groupRectangles(boxes, groupThreshold=1, eps=0.2)[0]
        
        return grouped_boxes

    def find_template_on_screen(self, template_name, threshold=0.8):
        """
        Find a single template and return its center coordinates.
        """
        if template_name not in self.templates:
            return None, 0
            
        template_img = self.templates[template_name]
        
        screenshot = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        
        result = cv2.matchTemplate(screenshot_cv, template_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            h, w = template_img.shape
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y), max_val
            
        return None, max_val

    def find_first_matching_template(self, candidate_list, threshold=0.8):
        """
        Takes a single screenshot and checks candidates in order of priority.
        candidate_list items can be:
          - A string: 'sinh.png'
          - A tuple/list: (item_id, ['sinh.png', 'gate_sinh.png']) or (item_id, 'sinh.png')
        Returns (matched_item, (center_x, center_y), confidence) or (None, None, 0)
        """
        screenshot = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        
        for candidate in candidate_list:
            if isinstance(candidate, (tuple, list)):
                cand_id = candidate[0]
                filenames = candidate[1]
                if isinstance(filenames, str):
                    filenames = [filenames]
            else:
                cand_id = candidate
                filenames = [candidate]

            for fname in filenames:
                if fname in self.templates:
                    template_img = self.templates[fname]
                    result = cv2.matchTemplate(screenshot_cv, template_img, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    if max_val >= threshold:
                        h, w = template_img.shape
                        center_x = max_loc[0] + w // 2
                        center_y = max_loc[1] + h // 2
                        return cand_id, (center_x, center_y), max_val

        return None, None, 0

