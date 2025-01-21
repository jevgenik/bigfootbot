import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class EdgeDetectionNode(Node):
    def __init__(self):
        super().__init__('edge_detection_node')
        self.sub_rgb = self.create_subscription(Image, '/color/image_raw', self.edge_detection_callback, 10)
        self.pub_lines = self.create_publisher(Image, 'road_lines', 10)  # Replacing road_edge
        self.pub_image_out = self.create_publisher(Image, 'image_out', 10)  # Overlayed road lines
        self.bridge = CvBridge()

    def edge_detection_callback(self, msg):
        # Convert ROS Image to OpenCV format
        rgb_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Convert to grayscale
        gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        blur_image = cv2.GaussianBlur(gray_image, (7, 7), 10)

        # Apply edge detection (Canny)
        edges = cv2.Canny(blur_image, 75, 150)

        # Detect lines using Hough Line Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, maxLineGap=30)

        # Create a blank image to draw lines
        line_image = np.zeros_like(rgb_image)

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green lines

        # Overlay road lines on the original image
        overlayed_image = cv2.addWeighted(rgb_image, 0.8, line_image, 1, 0)

        # Publish the road lines image
        line_msg = self.bridge.cv2_to_imgmsg(line_image, encoding='bgr8')
        self.pub_lines.publish(line_msg)

        # Publish the image with overlaid road lines
        overlayed_msg = self.bridge.cv2_to_imgmsg(overlayed_image, encoding='bgr8')
        self.pub_image_out.publish(overlayed_msg)

def main(args=None):
    rclpy.init(args=args)
    edge_detection_node = EdgeDetectionNode()
    rclpy.spin(edge_detection_node)
    edge_detection_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
