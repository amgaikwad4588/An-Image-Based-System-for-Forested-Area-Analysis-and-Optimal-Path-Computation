import io
import base64
import json
import math
import heapq
from typing import List, Dict, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
from scipy.ndimage import uniform_filter

app = Flask(__name__)
CORS(app)

# =============================================================================
# OPTIMAL PATHING API FUNCTIONS
# =============================================================================

def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(image)

def threshold_green_channel(rgb_image: np.ndarray) -> np.ndarray:
    rgb = rgb_image.astype(np.uint8)
    green_channel = rgb[:, :, 1].astype(np.float32)
    mean_green = float(np.mean(green_channel))
    threshold_value = mean_green / 1.5
    binary = np.where(green_channel > threshold_value, 255, 0).astype(np.uint8)
    return binary

def precompute_euclidean(rows: int, cols: int, target: Tuple[int, int]) -> np.ndarray:
    ti, tj = target
    ii, jj = np.meshgrid(np.arange(rows), np.arange(cols), indexing="ij")
    return np.sqrt((ii - ti) ** 2 + (jj - tj) ** 2)

def create_graph_costs(binary_image: np.ndarray, target: Tuple[int, int]) -> np.ndarray:
    rows, cols = binary_image.shape
    tree_count_density = 115.0 / (rows * cols) * 1000.0
    tcd_factor = math.exp(tree_count_density * 100.0)
    euclid = precompute_euclidean(rows, cols, target)

    # Neighborhood cost base term: higher cost through white (255), lower through black (0)
    base_cost = tcd_factor * (255 - binary_image.astype(np.float32))

    # Local density term using a small window average around each pixel
    avg_density = uniform_filter(255 - binary_image.astype(np.float32), size=5)
    density_term = 50000.0 * np.log(avg_density + 1.0)

    # Combine with squared euclidean to target for goal-oriented search bias
    costs = base_cost + (euclid ** 2) + density_term
    return costs

def dijkstra_path(costs: np.ndarray, start: Tuple[int, int], target: Tuple[int, int]) -> List[Tuple[int, int]]:
    rows, cols = costs.shape
    visited = np.zeros((rows, cols), dtype=bool)
    dist = np.full((rows, cols), np.inf, dtype=np.float64)
    parent_i = np.full((rows, cols), -1, dtype=np.int32)
    parent_j = np.full((rows, cols), -1, dtype=np.int32)

    si, sj = start
    ti, tj = target
    dist[si, sj] = 0.0
    pq: List[Tuple[float, int, int]] = [(0.0, si, sj)]

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]

    while pq:
        current_cost, i, j = heapq.heappop(pq)
        if visited[i, j]:
            continue
        visited[i, j] = True
        if (i, j) == (ti, tj):
            break

        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < rows and 0 <= nj < cols and not visited[ni, nj]:
                step_cost = costs[ni, nj]
                new_cost = current_cost + step_cost
                if new_cost < dist[ni, nj]:
                    dist[ni, nj] = new_cost
                    parent_i[ni, nj] = i
                    parent_j[ni, nj] = j
                    heapq.heappush(pq, (new_cost, ni, nj))

    # Reconstruct path
    path: List[Tuple[int, int]] = []
    i, j = ti, tj
    if parent_i[i, j] == -1 and (i, j) != (si, sj):
        return path  # no path
    while not (i == si and j == sj):
        path.append((i, j))
        pi, pj = parent_i[i, j], parent_j[i, j]
        if pi == -1 or pj == -1:
            break
        i, j = pi, pj
    path.append((si, sj))
    path.reverse()
    return path

def overlay_path_on_image(rgb_image: np.ndarray, path: List[Tuple[int, int]], color=(255, 0, 0)) -> Image.Image:
    image = Image.fromarray(rgb_image.copy())
    draw = ImageDraw.Draw(image)
    if len(path) >= 2:
        # Convert (row, col) to (x, y) = (col, row)
        points = [(int(c), int(r)) for r, c in path]
        draw.line(points, fill=color, width=3)
    return image

def process_image_and_compute_path(image_bytes: bytes, start: Optional[Tuple[int, int]] = None, target: Optional[Tuple[int, int]] = None) -> Tuple[str, dict]:
    rgb = load_image_from_bytes(image_bytes)
    rows, cols, _ = rgb.shape
    if start is None:
        start = (0, 0)
    if target is None:
        target = (rows - 1, cols - 1)

    binary = threshold_green_channel(rgb)
    costs = create_graph_costs(binary, target)
    path = dijkstra_path(costs, start, target)

    overlay = overlay_path_on_image(rgb, path)
    out_buf = io.BytesIO()
    overlay.save(out_buf, format="PNG")
    b64 = base64.b64encode(out_buf.getvalue()).decode("utf-8")

    # Simple metrics
    green_cover_pct = float(np.count_nonzero(binary) / (rows * cols) * 100.0)
    idle_land_pct = 100.0 - green_cover_pct

    meta = {
        "width": cols,
        "height": rows,
        "path_points": len(path),
        "green_cover_pct": round(green_cover_pct, 2),
        "idle_land_pct": round(idle_land_pct, 2),
    }
    return b64, meta

# =============================================================================
# TREE SPECIES IDENTIFICATION API FUNCTIONS
# =============================================================================

# Enhanced tree species database with 25+ species
TREE_SPECIES = {
    # Deciduous Trees
    'Oak': {
        'characteristics': ['broad leaves', 'lobed edges', 'strong trunk', 'spreading branches', 'acorns'],
        'color_range': [(40, 80, 30), (140, 180, 80)],
        'texture': 'rough',
        'confidence_base': 0.75,
        'category': 'deciduous'
    },
    'Maple': {
        'characteristics': ['palmate leaves', 'bright fall colors', 'symmetrical crown', 'helicopter seeds'],
        'color_range': [(50, 100, 30), (180, 220, 120)],
        'texture': 'moderate',
        'confidence_base': 0.8,
        'category': 'deciduous'
    },
    'Birch': {
        'characteristics': ['white bark', 'small leaves', 'slender trunk', 'catkins'],
        'color_range': [(70, 120, 50), (160, 200, 100)],
        'texture': 'smooth',
        'confidence_base': 0.7,
        'category': 'deciduous'
    },
    'Willow': {
        'characteristics': ['long drooping branches', 'narrow leaves', 'near water', 'flexible twigs'],
        'color_range': [(60, 100, 40), (140, 190, 90)],
        'texture': 'smooth',
        'confidence_base': 0.65,
        'category': 'deciduous'
    },
    'Elm': {
        'characteristics': ['oval leaves', 'serrated edges', 'vase shape', 'winged seeds'],
        'color_range': [(45, 90, 35), (130, 170, 85)],
        'texture': 'moderate',
        'confidence_base': 0.7,
        'category': 'deciduous'
    },
    'Ash': {
        'characteristics': ['compound leaves', 'opposite branching', 'diamond bark pattern'],
        'color_range': [(50, 95, 40), (140, 180, 90)],
        'texture': 'rough',
        'confidence_base': 0.68,
        'category': 'deciduous'
    },
    'Beech': {
        'characteristics': ['smooth gray bark', 'oval leaves', 'beech nuts', 'dense canopy'],
        'color_range': [(55, 105, 45), (150, 190, 95)],
        'texture': 'smooth',
        'confidence_base': 0.72,
        'category': 'deciduous'
    },
    'Cherry': {
        'characteristics': ['white/pink flowers', 'small red fruits', 'smooth bark', 'oval leaves'],
        'color_range': [(60, 110, 50), (160, 210, 110)],
        'texture': 'smooth',
        'confidence_base': 0.75,
        'category': 'deciduous'
    },
    'Apple': {
        'characteristics': ['white/pink flowers', 'round fruits', 'rough bark', 'oval leaves'],
        'color_range': [(65, 115, 55), (170, 220, 115)],
        'texture': 'rough',
        'confidence_base': 0.78,
        'category': 'deciduous'
    },
    'Poplar': {
        'characteristics': ['tall straight trunk', 'triangular leaves', 'catkins', 'fast growing'],
        'color_range': [(50, 100, 40), (140, 190, 100)],
        'texture': 'smooth',
        'confidence_base': 0.68,
        'category': 'deciduous'
    },
    
    # Coniferous Trees
    'Pine': {
        'characteristics': ['needle-like leaves', 'conical shape', 'evergreen', 'pine cones'],
        'color_range': [(25, 70, 25), (110, 160, 70)],
        'texture': 'smooth',
        'confidence_base': 0.85,
        'category': 'coniferous'
    },
    'Cedar': {
        'characteristics': ['scale-like leaves', 'pyramidal shape', 'aromatic', 'reddish bark'],
        'color_range': [(30, 80, 30), (120, 170, 80)],
        'texture': 'rough',
        'confidence_base': 0.8,
        'category': 'coniferous'
    },
    'Spruce': {
        'characteristics': ['short needles', 'pyramidal shape', 'hanging cones', 'blue-green color'],
        'color_range': [(20, 60, 20), (100, 150, 60)],
        'texture': 'smooth',
        'confidence_base': 0.82,
        'category': 'coniferous'
    },
    'Fir': {
        'characteristics': ['flat needles', 'upright cones', 'pyramidal shape', 'soft needles'],
        'color_range': [(25, 65, 25), (105, 155, 65)],
        'texture': 'smooth',
        'confidence_base': 0.8,
        'category': 'coniferous'
    },
    'Hemlock': {
        'characteristics': ['short flat needles', 'drooping branches', 'small cones', 'dark green'],
        'color_range': [(20, 55, 20), (90, 140, 55)],
        'texture': 'smooth',
        'confidence_base': 0.75,
        'category': 'coniferous'
    },
    'Juniper': {
        'characteristics': ['scale-like leaves', 'blue berries', 'irregular shape', 'aromatic'],
        'color_range': [(30, 70, 30), (110, 160, 70)],
        'texture': 'rough',
        'confidence_base': 0.7,
        'category': 'coniferous'
    },
    'Larch': {
        'characteristics': ['deciduous conifer', 'soft needles', 'golden fall color', 'small cones'],
        'color_range': [(40, 90, 40), (130, 180, 90)],
        'texture': 'smooth',
        'confidence_base': 0.72,
        'category': 'coniferous'
    },
    
    # Tropical/Subtropical Trees
    'Palm': {
        'characteristics': ['fan-shaped leaves', 'tall trunk', 'tropical', 'coconut-like fruits'],
        'color_range': [(60, 120, 50), (160, 210, 110)],
        'texture': 'rough',
        'confidence_base': 0.9,
        'category': 'tropical'
    },
    'Eucalyptus': {
        'characteristics': ['smooth bark', 'long narrow leaves', 'aromatic', 'gum nuts'],
        'color_range': [(50, 110, 45), (140, 200, 105)],
        'texture': 'smooth',
        'confidence_base': 0.8,
        'category': 'tropical'
    },
    'Bamboo': {
        'characteristics': ['hollow stems', 'narrow leaves', 'clumping growth', 'fast growing'],
        'color_range': [(40, 90, 35), (120, 180, 85)],
        'texture': 'smooth',
        'confidence_base': 0.85,
        'category': 'tropical'
    },
    'Mango': {
        'characteristics': ['large oval leaves', 'yellow fruits', 'dense canopy', 'tropical'],
        'color_range': [(55, 105, 45), (150, 200, 100)],
        'texture': 'moderate',
        'confidence_base': 0.75,
        'category': 'tropical'
    },
    'Banyan': {
        'characteristics': ['aerial roots', 'large canopy', 'fig fruits', 'tropical'],
        'color_range': [(45, 95, 40), (130, 180, 90)],
        'texture': 'rough',
        'confidence_base': 0.7,
        'category': 'tropical'
    },
    
    # Flowering Trees
    'Magnolia': {
        'characteristics': ['large white/pink flowers', 'oval leaves', 'smooth bark', 'fragrant'],
        'color_range': [(60, 115, 50), (160, 210, 110)],
        'texture': 'smooth',
        'confidence_base': 0.8,
        'category': 'flowering'
    },
    'Dogwood': {
        'characteristics': ['white/pink flowers', 'oval leaves', 'red berries', 'understory tree'],
        'color_range': [(55, 110, 45), (150, 200, 105)],
        'texture': 'smooth',
        'confidence_base': 0.75,
        'category': 'flowering'
    },
    'Redbud': {
        'characteristics': ['pink/purple flowers', 'heart-shaped leaves', 'small tree', 'early spring'],
        'color_range': [(50, 100, 40), (140, 190, 95)],
        'texture': 'smooth',
        'confidence_base': 0.72,
        'category': 'flowering'
    },
    'Crabapple': {
        'characteristics': ['white/pink flowers', 'small red fruits', 'oval leaves', 'ornamental'],
        'color_range': [(60, 120, 50), (160, 220, 115)],
        'texture': 'moderate',
        'confidence_base': 0.78,
        'category': 'flowering'
    }
}

def analyze_image_features(image: np.ndarray) -> Dict:
    """Analyze image features for tree species identification"""
    # Convert to different color spaces for analysis
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    
    # Extract color features
    mean_rgb = np.mean(image, axis=(0, 1))
    mean_hsv = np.mean(hsv, axis=(0, 1))
    
    # Analyze texture using Laplacian variance
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    texture_variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Analyze shape characteristics
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calculate shape features
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
        else:
            circularity = 0
    else:
        circularity = 0
    
    return {
        'mean_rgb': mean_rgb.tolist(),
        'mean_hsv': mean_hsv.tolist(),
        'texture_variance': float(texture_variance),
        'circularity': float(circularity),
        'brightness': float(np.mean(gray))
    }

def calculate_species_confidence(features: Dict, species: str) -> float:
    """Enhanced confidence calculation with multiple feature analysis"""
    species_info = TREE_SPECIES[species]
    confidence = species_info['confidence_base']
    
    # Enhanced color matching with HSV analysis
    mean_rgb = np.array(features['mean_rgb'])
    mean_hsv = np.array(features['mean_hsv'])
    color_range = species_info['color_range']
    min_color = np.array(color_range[0])
    max_color = np.array(color_range[1])
    
    # RGB color matching with distance calculation
    rgb_distance = np.linalg.norm(mean_rgb - np.mean([min_color, max_color], axis=0))
    max_distance = np.linalg.norm(max_color - min_color)
    color_score = max(0, 1 - (rgb_distance / max_distance))
    confidence += color_score * 0.15
    
    # HSV-based seasonal analysis
    hue = mean_hsv[0]
    saturation = mean_hsv[1]
    value = mean_hsv[2]
    
    # Seasonal color adjustments
    if species_info['category'] == 'deciduous':
        if 0 < hue < 30 or 330 < hue < 360:  # Red/orange fall colors
            confidence += 0.1
        elif 60 < hue < 120:  # Green summer colors
            confidence += 0.08
    elif species_info['category'] == 'coniferous':
        if 60 < hue < 120 and saturation > 30:  # Green coniferous
            confidence += 0.1
    
    # Enhanced texture analysis
    texture_var = features['texture_variance']
    if species_info['texture'] == 'rough':
        if texture_var > 1200:
            confidence += 0.08
        elif texture_var > 800:
            confidence += 0.05
    elif species_info['texture'] == 'smooth':
        if texture_var < 400:
            confidence += 0.08
        elif texture_var < 600:
            confidence += 0.05
    elif species_info['texture'] == 'moderate':
        if 600 < texture_var < 1000:
            confidence += 0.06
    
    # Enhanced shape analysis
    circularity = features['circularity']
    if species_info['category'] == 'coniferous':
        if circularity > 0.4:  # Very conical
            confidence += 0.12
        elif circularity > 0.25:  # Moderately conical
            confidence += 0.08
    elif species_info['category'] == 'deciduous':
        if 0.15 < circularity < 0.5:  # Broad, rounded shapes
            confidence += 0.1
    elif species_info['category'] == 'tropical':
        if circularity > 0.3:  # Palm-like or columnar
            confidence += 0.1
    
    # Brightness analysis with category-specific adjustments
    brightness = features['brightness']
    if species in ['Birch', 'Aspen'] and brightness > 160:  # Very light bark
        confidence += 0.12
    elif species in ['Cedar', 'Pine', 'Spruce'] and brightness < 90:  # Dark coniferous
        confidence += 0.1
    elif species_info['category'] == 'tropical' and brightness > 120:  # Bright tropical
        confidence += 0.08
    
    # Size estimation based on image dimensions (if available)
    if 'image_size' in features:
        width, height = features['image_size']
        aspect_ratio = width / height
        
        if species in ['Palm', 'Poplar'] and aspect_ratio < 0.8:  # Tall and narrow
            confidence += 0.08
        elif species in ['Oak', 'Maple'] and 0.8 < aspect_ratio < 1.2:  # Broad and round
            confidence += 0.06
    
    # Category-based confidence boost
    if species_info['category'] == 'coniferous':
        confidence += 0.05  # Conifers are generally easier to identify
    elif species_info['category'] == 'tropical':
        confidence += 0.03  # Distinctive tropical features
    
    return min(confidence, 1.0)  # Cap at 1.0

def identify_tree_species(image: np.ndarray) -> List[Dict]:
    """Identify tree species in the image"""
    features = analyze_image_features(image)
    
    species_predictions = []
    for species in TREE_SPECIES.keys():
        confidence = calculate_species_confidence(features, species)
        species_predictions.append({
            'species': species,
            'confidence': round(confidence, 3),
            'characteristics': TREE_SPECIES[species]['characteristics']
        })
    
    # Sort by confidence
    species_predictions.sort(key=lambda x: x['confidence'], reverse=True)
    return species_predictions

def draw_species_annotations(image: np.ndarray, predictions: List[Dict]) -> Image.Image:
    """Draw species identification results on the image"""
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Draw top 3 predictions
    y_offset = 10
    for i, pred in enumerate(predictions[:3]):
        text = f"{pred['species']}: {pred['confidence']:.1%}"
        color = (255, 0, 0) if i == 0 else (0, 0, 255)  # Red for top prediction
        
        # Draw background rectangle
        bbox = draw.textbbox((10, y_offset), text, font=font)
        draw.rectangle(bbox, fill=(255, 255, 255, 200))
        
        # Draw text
        draw.text((10, y_offset), text, fill=color, font=font)
        y_offset += 30
    
    return pil_image

def process_image_for_species(image_bytes: bytes) -> Tuple[str, Dict]:
    """Process uploaded image for tree species identification"""
    # Load image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_array = np.array(image)
    
    # Identify species
    species_predictions = identify_tree_species(image_array)
    
    # Draw annotations
    annotated_image = draw_species_annotations(image_array, species_predictions)
    
    # Convert to base64
    output_buffer = io.BytesIO()
    annotated_image.save(output_buffer, format="PNG")
    b64_image = base64.b64encode(output_buffer.getvalue()).decode("utf-8")
    
    # Prepare metadata
    metadata = {
        "predictions": species_predictions,
        "top_prediction": species_predictions[0] if species_predictions else None,
        "total_species_analyzed": len(TREE_SPECIES)
    }
    
    return b64_image, metadata

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/process', methods=['POST'])
def process_optimal_path():
    """API endpoint for optimal pathing"""
    if "image" not in request.files:
        return jsonify({"error": "Missing file field 'image'"}), 400
    file = request.files["image"]
    start_i = request.form.get("start_i", type=int)
    start_j = request.form.get("start_j", type=int)
    target_i = request.form.get("target_i", type=int)
    target_j = request.form.get("target_j", type=int)
    start = (start_i, start_j) if start_i is not None and start_j is not None else None
    target = (target_i, target_j) if target_i is not None and target_j is not None else None

    image_bytes = file.read()
    try:
        b64, meta = process_image_and_compute_path(image_bytes, start, target)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "image_base64": b64,
        "meta": meta,
    })

@app.route('/identify_species', methods=['POST'])
def identify_species():
    """API endpoint for tree species identification"""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image file selected"}), 400
    
    try:
        image_bytes = file.read()
        b64_image, metadata = process_image_for_species(image_bytes)
        
        return jsonify({
            "success": True,
            "annotated_image": b64_image,
            "metadata": metadata
        })
    
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/species_info', methods=['GET'])
def get_species_info():
    """Get information about available tree species"""
    return jsonify({
        "available_species": list(TREE_SPECIES.keys()),
        "species_details": TREE_SPECIES
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "services": ["optimal_pathing", "tree_species_identification"],
        "version": "1.0.0"
    })

if __name__ == '__main__':
    print("EcoView Imaging - Unified API Server")
    print("=" * 40)
    print("Available endpoints:")
    print("  POST /process              - Optimal pathing")
    print("  POST /identify_species     - Tree species identification")
    print("  GET  /species_info         - Available species list")
    print("  GET  /health               - Health check")
    print("=" * 40)
    print("Server starting on http://127.0.0.1:8000")
    app.run(host='127.0.0.1', port=8000, debug=True)
