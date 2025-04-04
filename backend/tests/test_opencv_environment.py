import pytest
import cv2
import numpy as np
import os

class TestOpenCVEnvironment:
    """OpenCV环境测试类"""
    
    def setup_method(self):
        """测试前创建测试图像"""
        # 创建测试图像目录
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_images')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # 创建一个测试图像
        self.test_image = np.zeros((300, 400, 3), dtype=np.uint8)
        # 绘制一些基本图形
        cv2.rectangle(self.test_image, (50, 50), (200, 200), (0, 255, 0), 2)
        cv2.circle(self.test_image, (300, 150), 50, (0, 0, 255), -1)
        cv2.putText(self.test_image, 'OpenCV Test', (100, 250), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 保存测试图像
        self.test_image_path = os.path.join(self.test_dir, 'test.jpg')
        cv2.imwrite(self.test_image_path, self.test_image)

    def teardown_method(self):
        """测试后清理测试文件"""
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_basic_operations(self):
        """测试基本图像操作"""
        # 读取图像
        img = cv2.imread(self.test_image_path)
        assert img is not None, "图像读取失败"
        assert img.shape == (300, 400, 3), "图像尺寸不正确"

        # 图像缩放
        resized = cv2.resize(img, (200, 150))
        assert resized.shape == (150, 200, 3), "图像缩放失败"

        # 图像旋转
        matrix = cv2.getRotationMatrix2D((img.shape[1]/2, img.shape[0]/2), 45, 1.0)
        rotated = cv2.warpAffine(img, matrix, (img.shape[1], img.shape[0]))
        assert rotated.shape == img.shape, "图像旋转失败"

        # 图像模糊
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        assert blurred.shape == img.shape, "高斯模糊失败"

    def test_color_operations(self):
        """测试颜色空间操作"""
        img = cv2.imread(self.test_image_path)
        
        # BGR转灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        assert len(gray.shape) == 2, "灰度转换失败"
        
        # BGR转HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        assert hsv.shape == img.shape, "HSV转换失败"
        
        # 颜色阈值处理
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        assert mask.shape == (300, 400), "颜色阈值处理失败"

    def test_feature_detection(self):
        """测试特征检测功能"""
        img = cv2.imread(self.test_image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 边缘检测
        edges = cv2.Canny(gray, 100, 200)
        assert edges.shape == gray.shape, "边缘检测失败"
        
        # 角点检测
        corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
        assert corners is not None, "角点检测失败"
        
        # 特征检测器
        orb = cv2.ORB_create()
        keypoints = orb.detect(gray, None)
        assert len(keypoints) > 0, "ORB特征检测失败"

    def test_image_processing(self):
        """测试图像处理功能"""
        img = cv2.imread(self.test_image_path)
        
        # 图像二值化
        _, binary = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 
                                127, 255, cv2.THRESH_BINARY)
        assert binary.shape == (300, 400), "图像二值化失败"
        
        # 形态学操作
        kernel = np.ones((5,5), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=1)
        eroded = cv2.erode(binary, kernel, iterations=1)
        assert dilated.shape == binary.shape, "膨胀操作失败"
        assert eroded.shape == binary.shape, "腐蚀操作失败"
        
        # 轮廓检测
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, 
                                     cv2.CHAIN_APPROX_SIMPLE)
        assert len(contours) > 0, "轮廓检测失败"

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 