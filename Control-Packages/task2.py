import cv2


def is_center_in_roi(corners, roi_bounds):
    """Check if the center of a detected tag falls within the ROI bounding box."""
    tag_center_x = int(corners[:, 0].mean())
    tag_center_y = int(corners[:, 1].mean())

    x1, y1, x2, y2 = roi_bounds
    return x1 <= tag_center_x <= x2 and y1 <= tag_center_y <= y2


def find_working_cameras(max_tested=10):
    """Find all valid camera configurations (index + backend) on Windows 11."""
    found_cams = []

    # Backends to probe on Windows
    backends = [
        ("MSMF", cv2.CAP_MSMF),
        ("DSHOW", cv2.CAP_DSHOW),
        ("ANY", cv2.CAP_ANY),
    ]

    for index in range(max_tested):
        for backend_name, backend_flag in backends:
            cap = cv2.VideoCapture(index, backend_flag)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    already_added = any(c["index"] == index for c in found_cams)
                    if not already_added:
                        found_cams.append(
                            {
                                "index": index,
                                "backend_name": backend_name,
                                "backend_flag": backend_flag,
                            }
                        )
            cap.release()

    return (
        found_cams
        if found_cams
        else [{"index": 0, "backend_name": "ANY", "backend_flag": cv2.CAP_ANY}]
    )


def open_camera_stream(cam_info):
    """Attempt to open VideoCapture with backend fallback."""
    cap = cv2.VideoCapture(cam_info["index"], cam_info["backend_flag"])
    if not cap.isOpened():
        cap = cv2.VideoCapture(cam_info["index"])
    return cap


def main():
    print("Scanning system for connected cameras (Built-in + USB)...")
    available_cameras = find_working_cameras()

    current_cam_idx = 0
    cam_info = available_cameras[current_cam_idx]
    cap = open_camera_stream(cam_info)

    if not cap.isOpened():
        print(f"Error: Could not open camera at index {cam_info['index']}.")
        return

    # Load AprilTag 25h9 dictionary
    dictionary = cv2.aruco.getPredefinedDictionary(
        cv2.aruco.DICT_APRILTAG_36h11
    )
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    global_min_id = None
    global_max_id = None

    print("\n================ SYSTEM READY ================")
    print(f"Detected {len(available_cameras)} active camera device(s):")
    for i, cam in enumerate(available_cameras):
        print(
            f"  [{i}] Index: {cam['index']} | Backend: {cam['backend_name']}"
        )

    print("\nControls:")
    print("  'H' / 'h': Toggle/Switch between cameras")
    print("  'G' / 'g': Print current Min/Max IDs to console")
    print("  'R' / 'r': Reset tracked min/max memory")
    print("  'Q' / 'q': Quit application")
    print("==============================================\n")

    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            cv2.waitKey(100)
            continue

        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        # Define central ROI box
        roi_size = 300
        roi_x1 = center_x - (roi_size // 2)
        roi_y1 = center_y - (roi_size // 2)
        roi_x2 = center_x + (roi_size // 2)
        roi_y2 = center_y + (roi_size // 2)
        roi_bounds = (roi_x1, roi_y1, roi_x2, roi_y2)

        # Draw ROI Box (Cyan) & Crosshair (Red)
        cv2.rectangle(
            frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (255, 255, 0), 1
        )

        crosshair_size = 20
        cv2.line(
            frame,
            (center_x - crosshair_size, center_y),
            (center_x + crosshair_size, center_y),
            (0, 0, 255),
            2,
        )
        cv2.line(
            frame,
            (center_x, center_y - crosshair_size),
            (center_x, center_y + crosshair_size),
            (0, 0, 255),
            2,
        )

        # Overlay active camera info top-left
        cv2.putText(
            frame,
            f"Cam Index: {cam_info['index']} ({cam_info['backend_name']})",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None and len(ids) > 0:
            valid_corners = []
            valid_ids = []

            flat_ids = ids.flatten().tolist()

            for i, corner in enumerate(corners):
                if is_center_in_roi(corner[0], roi_bounds):
                    valid_corners.append(corner)
                    valid_ids.append(flat_ids[i])

            if len(valid_ids) > 0:
                current_min = min(valid_ids)
                current_max = max(valid_ids)

                if global_min_id is None or current_min < global_min_id:
                    global_min_id = current_min

                if global_max_id is None or current_max > global_max_id:
                    global_max_id = current_max

                for i, corner in enumerate(valid_corners):
                    tag_corners = corner[0].astype(int)

                    cv2.polylines(
                        frame,
                        [tag_corners],
                        isClosed=True,
                        color=(0, 255, 0),
                        thickness=2,
                    )

                    top_y = min(tag_corners[:, 1])
                    top_x = int(tag_corners[:, 0].mean())

                    cv2.putText(
                        frame,
                        "FOUND",
                        (top_x - 30, max(20, top_y - 30)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )

                    cv2.putText(
                        frame,
                        f"Min:{global_min_id} Max:{global_max_id}",
                        (top_x - 55, max(40, top_y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 0),
                        2,
                    )

        cv2.imshow("AprilTag Center Scanner", frame)

        key = cv2.waitKey(1) & 0xFF

        # Toggle camera on 'H'
        if key in (ord("h"), ord("H")):
            if len(available_cameras) <= 1:
                print(
                    "\n[Camera Switch] Re-scanning for newly plugged USB cameras..."
                )
                available_cameras = find_working_cameras()

            if len(available_cameras) > 1:
                current_cam_idx = (current_cam_idx + 1) % len(available_cameras)
                cam_info = available_cameras[current_cam_idx]

                cap.release()
                cap = open_camera_stream(cam_info)

                print(
                    f"\n[Camera Switch] Switched to Camera Index {cam_info['index']} ({cam_info['backend_name']})"
                )
            else:
                print(
                    "[Camera Switch] Only 1 camera found. Ensure Windows privacy settings allow desktop apps to access the USB camera."
                )

        # Print report on 'G'
        elif key in (ord("g"), ord("G")):
            print("\n================ CONSOLE REPORT ================")
            if global_min_id is not None and global_max_id is not None:
                print(f"Current Smallest Tag ID (Min): {global_min_id}")
                print(f"Current Largest Tag ID  (Max): {global_max_id}")
            else:
                print("No AprilTags have been scanned yet.")
            print("================================================\n")

        # Reset on 'R'
        elif key in (ord("r"), ord("R")):
            global_min_id = None
            global_max_id = None
            print("\n[System] Global Min/Max IDs reset.\n")

        # Quit on 'Q'
        elif key in (ord("q"), ord("Q")):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()