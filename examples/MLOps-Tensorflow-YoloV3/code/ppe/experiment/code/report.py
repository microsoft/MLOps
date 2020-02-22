import glob
import json
import os
import shutil
import operator
import sys
import argparse
import cv2
import matplotlib.pyplot as plt
from scripts.compress import zipFolder, unzipFolder
from azureml.core import Model, Run, Datastore


class mAP():
    
    def __init__(self):
        self._parser = argparse.ArgumentParser("mAP")
        self._parser.add_argument("--release_id", type=str, help="The ID of the release triggering this pipeline run")
        self._parser.add_argument("--model_name", type=str, help="Name of the tf model")
        self._parser.add_argument("--ckpt_path", type=str, help="Chekpoint path", default="checkpoint/yolov3.ckpt")
        self._parser.add_argument("--datastore", type=str, help="Name of the datastore", default="epis_datastore")
        self._parser.add_argument("--storage_container", type=str, help="Name of the storage container", default="ppe")
        self._parser.add_argument('-na', '--no-animation', help="no animation is shown.", action="store_true")
        self._parser.add_argument('-np', '--no-plot', help="no plot is shown.", action="store_true")
        self._parser.add_argument('-q', '--quiet', help="minimalistic console output.", action="store_true")
        self._parser.add_argument('-i', '--ignore', nargs='+', type=str, help="ignore a list of classes.")
        self._parser.add_argument('--set-class-iou', nargs='+', type=str, help="set IoU for a specific class.")

        self._args = self._parser.parse_args()
        self._run = Run.get_context()
        self._exp = self._run.experiment
        self._ws = self._run.experiment.workspace
        self._datastore = Datastore.get(self._ws, datastore_name=self._args.datastore)

        self._MINOVERLAP = 0.5
      
    def main(self):
        if self._args.ignore is None:
            self._args.ignore = []

        specific_iou_flagged = False
        if self._args.set_class_iou is not None:
            specific_iou_flagged = True

        img_path = 'images'
        if os.path.exists(img_path): 
            for dirpath, dirnames, files in os.walk(img_path):
                if not files:
                    args.no_animation = True
        else:
            self._args.no_animation = True

        show_animation = False
        if not self._args.no_animation:
            try:
                show_animation = True
            except ImportError:
                print("\"opencv-python\" not found, please install to visualize the results.")
                self._args.no_animation = True

        draw_plot = False
        if not self._args.no_plot:
            try:
                draw_plot = True
            except ImportError:
                print("\"matplotlib\" not found, please install it to get the resulting plots.")
                args.no_plot = True
            
        all_runs = self._exp.get_runs(properties={"release_id": self._args.release_id, "run_type": "eval"},
                                include_children=True)
        eval_run = next(all_runs)
        print(f'New Run found with Run ID of: {eval_run.id}')

        eval_run.download_file(name="grtruth.zip", output_file_path=".")
        unzipFolder('grtruth.zip')

        eval_run.download_file(name="predicts.zip", output_file_path=".")
        unzipFolder('predicts.zip')

        tmp_files_path, results_files_path = self.__create_tmp_paths(draw_plot, show_animation)
        gt_classes, gt_counter_per_class, n_classes, ground_truth_files_list = self.__ground_truth(tmp_files_path)
        predicted_files_list = self.__predicted(gt_classes, tmp_files_path)
        count_true_positives, ap_dictionary, mAP = self.__calculatemAP(draw_plot, show_animation, img_path,
                                                gt_classes, n_classes, gt_counter_per_class,
                                                results_files_path, gt_classes, tmp_files_path,
                                                specific_iou_flagged)
        shutil.rmtree(tmp_files_path)
        pred_classes, pred_counter_per_class = self.__countTotalPredictions(predicted_files_list)
        self.__plotTotalNumberOccurenceGroundTruth(draw_plot, ground_truth_files_list, n_classes,
                                                results_files_path, gt_counter_per_class)
        self.__writeGroundTruthObjects(results_files_path, gt_counter_per_class)
        self.__countingTruePositives(pred_classes, gt_classes, count_true_positives)
        self.__writePredictedObjects(results_files_path, pred_classes, pred_counter_per_class, count_true_positives)
        self.__plotTotalNumberOcurrencesPredicted(draw_plot, predicted_files_list, pred_counter_per_class, results_files_path, count_true_positives)
        self.__plotmAP(draw_plot, results_files_path, ap_dictionary, n_classes, mAP)

        eval_run.download_file(name="model.zip", output_file_path=".")
        unzipFolder('model.zip')

        self._run.upload_file(name='saved_model.pb', path_or_stream="models/saved_model.pb")

        self._run.register_model(
            model_name = self._args.model_name,
            model_path = self._args.model_name,
            properties = {"release_id": self._args.release_id},
            tags= {"mAP": f"{mAP*100:.2f}%"}
            )
        print("Registered model!")

        zipFolder("report.zip", "mAP/results")

        self._run.upload_file(name='report.zip', path_or_stream="report.zip")
        print(f"Uploaded the report to experiment {self._run.experiment.name}")

        print("Following files are uploaded")
        print(self._run.get_file_names())

        self._run.add_properties({"release_id": self._args.release_id, "run_type": "report"})
        print(f"added properties: {self._run.properties}")

        self._run.complete()


    def __create_tmp_paths(self, draw_plot, show_animation):
        tmp_files_path = "mAP/tmp_files"
        if not os.path.exists(tmp_files_path):
            os.makedirs(tmp_files_path)
        results_files_path = "mAP/results"
        if os.path.exists(results_files_path):
            shutil.rmtree(results_files_path)

        os.makedirs(results_files_path)
        if draw_plot:
            os.makedirs(results_files_path + "/classes")
        if show_animation:
            os.makedirs(results_files_path + "/images")
            os.makedirs(results_files_path + "/images/single_predictions")
        return tmp_files_path, results_files_path

    
    def __ground_truth(self, tmp_files_path):
        ground_truth_files_list = glob.glob('mAP/ground-truth/*.txt')
        if len(ground_truth_files_list) == 0:
            self.__error("Error: No ground-truth files found!")
        ground_truth_files_list.sort()
        gt_counter_per_class = {}

        for txt_file in ground_truth_files_list:
            file_id = txt_file.split(".txt",1)[0]
            file_id = os.path.basename(os.path.normpath(file_id))
            if not os.path.exists('mAP/predicted/' + file_id + ".txt"):
                error_msg = "Error. File not found: predicted/" +  file_id + ".txt\n"
                error_msg += "(You can avoid this error message by running extra/intersect-gt-and-pred.py)"
                self.__error(error_msg)
            lines_list = self.__file_lines_to_list(txt_file)
            bounding_boxes = []
            is_difficult = False
            for line in lines_list:
                try:
                    if "difficult" in line:
                        class_name, left, top, right, bottom, _difficult = line.split()
                        is_difficult = True
                    else:
                        class_name, left, top, right, bottom = line.split()
                except ValueError:
                    error_msg = "Error: File " + txt_file + " in the wrong format.\n"
                    error_msg += " Expected: <class_name> <left> <top> <right> <bottom> ['difficult']\n"
                    error_msg += " Received: " + line
                    error_msg += "\n\nIf you have a <class_name> with spaces between words you should remove them\n"
                    error_msg += "by running the script \"remove_space.py\" or \"rename_class.py\" in the \"extra/\" folder."
                    self.__error(error_msg)
                if class_name in self._args.ignore:
                    continue
                bbox = left + " " + top + " " + right + " " +bottom
                if is_difficult:
                    bounding_boxes.append({"class_name":class_name, "bbox":bbox, "used":False, "difficult":True})
                    is_difficult = False
                else:
                    bounding_boxes.append({"class_name":class_name, "bbox":bbox, "used":False})
                    if class_name in gt_counter_per_class:
                        gt_counter_per_class[class_name] += 1
                    else:
                        gt_counter_per_class[class_name] = 1
            with open(tmp_files_path + "/" + file_id + "_ground_truth.json", 'w') as outfile:
                json.dump(bounding_boxes, outfile)
        gt_classes = list(gt_counter_per_class.keys())
        gt_classes = sorted(gt_classes)
        n_classes = len(gt_classes)
        return gt_classes, gt_counter_per_class, n_classes, ground_truth_files_list


    def __check_format_flag(self, specific_iou_flagged, gt_classes):
        if specific_iou_flagged:
            n_args = len(self._args.set_class_iou)
            error_msg = \
                '\n --set-class-iou [class_1] [IoU_1] [class_2] [IoU_2] [...]'
            if n_args % 2 != 0:
                self.__error('Error, missing arguments. Flag usage:' + error_msg)
            specific_iou_classes = self._args.set_class_iou[::2]
            iou_list = self._args.set_class_iou[1::2]
            if len(specific_iou_classes) != len(iou_list):
                self.__error('Error, missing arguments. Flag usage:' + error_msg)
            for tmp_class in specific_iou_classes:
                if tmp_class not in gt_classes:
                    self.error('Error, unknown class \"' + tmp_class + '\". Flag usage:' + error_msg)
            for num in iou_list:
                if not self.__is_float_between_0_and_1(num):
                    self.__error('Error, IoU must be between 0.0 and 1.0. Flag usage:' + error_msg)
            return specific_iou_classes, iou_list

    
    def __predicted(self, gt_classes, tmp_files_path):
        predicted_files_list = glob.glob('mAP/predicted/*.txt')
        predicted_files_list.sort()
        for class_index, class_name in enumerate(gt_classes):
            bounding_boxes = []
            for txt_file in predicted_files_list:
                file_id = txt_file.split(".txt",1)[0]
                file_id = os.path.basename(os.path.normpath(file_id))
                if class_index == 0:
                    if not os.path.exists('mAP/ground-truth/' + file_id + ".txt"):
                        error_msg = "Error. File not found: ground-truth/" +  file_id + ".txt\n"
                        error_msg += "(You can avoid this error message by running extra/intersect-gt-and-pred.py)"
                        self.__error(error_msg)
                lines = self.__file_lines_to_list(txt_file)
                for line in lines:
                    try:
                        tmp_class_name, confidence, left, top, right, bottom = line.split()
                    except ValueError:
                        error_msg = "Error: File " + txt_file + " in the wrong format.\n"
                        error_msg += " Expected: <class_name> <confidence> <left> <top> <right> <bottom>\n"
                        error_msg += " Received: " + line
                        self.__error(error_msg)
                    if tmp_class_name == class_name:
                        bbox = left + " " + top + " " + right + " " +bottom
                        bounding_boxes.append({"confidence":confidence, "file_id":file_id, "bbox":bbox})
            bounding_boxes.sort(key=lambda x:float(x['confidence']), reverse=True)
            with open(tmp_files_path + "/" + class_name + "_predictions.json", 'w') as outfile:
                json.dump(bounding_boxes, outfile)
        return predicted_files_list
    
    def __calculatemAP(self, draw_plot, show_animation, img_path, specific_iou_classes, n_classes, gt_counter_per_class, results_files_path, gt_classes, tmp_files_path, specific_iou_flagged):
        sum_AP = 0.0
        ap_dictionary = {}
        with open(results_files_path + "/results.txt", 'w') as results_file:
            results_file.write("# AP and precision/recall per class\n")
            count_true_positives = {}
            for class_index, class_name in enumerate(gt_classes):
                count_true_positives[class_name] = 0
                predictions_file = tmp_files_path + "/" + class_name + "_predictions.json"
                predictions_data = json.load(open(predictions_file))


                nd = len(predictions_data)
                tp = [0] * nd
                fp = [0] * nd
                for idx, prediction in enumerate(predictions_data):
                    file_id = prediction["file_id"]
                    if show_animation:
                        ground_truth_img = glob.glob1(img_path, file_id + ".*")
                        if len(ground_truth_img) == 0:
                            self.__error("Error. Image not found with id: " + file_id)
                        elif len(ground_truth_img) > 1:
                            self.__error("Error. Multiple image with id: " + file_id)
                        else:
                            img = cv2.imread(img_path + "/" + ground_truth_img[0])
                            img_cumulative_path = results_files_path + "/images/" + ground_truth_img[0]
                            if os.path.isfile(img_cumulative_path):
                                img_cumulative = cv2.imread(img_cumulative_path)
                            else:
                                img_cumulative = img.copy()
                            bottom_border = 60
                            BLACK = [0, 0, 0]
                            img = cv2.copyMakeBorder(img, 0, bottom_border, 0, 0, cv2.BORDER_CONSTANT, value=BLACK)
                    gt_file = tmp_files_path + "/" + file_id + "_ground_truth.json"
                    ground_truth_data = json.load(open(gt_file))
                    ovmax = -1
                    gt_match = -1
                    bb = [ float(x) for x in prediction["bbox"].split() ]
                    for obj in ground_truth_data:
                        if obj["class_name"] == class_name:
                            bbgt = [ float(x) for x in obj["bbox"].split() ]
                            bi = [max(bb[0],bbgt[0]), max(bb[1],bbgt[1]), min(bb[2],bbgt[2]), min(bb[3],bbgt[3])]
                            iw = bi[2] - bi[0] + 1
                            ih = bi[3] - bi[1] + 1
                            if iw > 0 and ih > 0:
                                ua = (bb[2] - bb[0] + 1) * (bb[3] - bb[1] + 1) + (bbgt[2] - bbgt[0]
                                        + 1) * (bbgt[3] - bbgt[1] + 1) - iw * ih
                                ov = iw * ih / ua
                                if ov > ovmax:
                                    ovmax = ov
                                    gt_match = obj

                    if show_animation:
                        status = "NO MATCH FOUND!"
                    min_overlap = self._MINOVERLAP
                    if ovmax >= min_overlap:
                        if "difficult" not in gt_match:
                            if not bool(gt_match["used"]):
                                tp[idx] = 1
                                gt_match["used"] = True
                                count_true_positives[class_name] += 1
                                with open(gt_file, 'w') as f:
                                    f.write(json.dumps(ground_truth_data))
                                if show_animation:
                                    status = "MATCH!"
                            else:
                                fp[idx] = 1
                                if show_animation:
                                    status = "REPEATED MATCH!"
                    else:
                        fp[idx] = 1
                        if ovmax > 0:
                            status = "INSUFFICIENT OVERLAP"

                    if show_animation:
                        height, widht = img.shape[:2]
                        white = (255,255,255)
                        light_blue = (255,200,100)
                        green = (0,255,0)
                        light_red = (30,30,255)
                        margin = 10
                        v_pos = int(height - margin - (bottom_border / 2))
                        text = "Image: " + ground_truth_img[0] + " "
                        img, line_width = self.__draw_text_in_image(img, text, (margin, v_pos), white, 0)
                        text = "Class [" + str(class_index) + "/" + str(n_classes) + "]: " + class_name + " "
                        img, line_width = self.__draw_text_in_image(img, text, (margin + line_width, v_pos), light_blue, line_width)
                        if ovmax != -1:
                            color = light_red
                            if status == "INSUFFICIENT OVERLAP":
                                text = "IoU: {0:.2f}% ".format(ovmax*100) + "< {0:.2f}% ".format(min_overlap*100)
                            else:
                                text = "IoU: {0:.2f}% ".format(ovmax*100) + ">= {0:.2f}% ".format(min_overlap*100)
                                color = green
                            img, _ = self.__draw_text_in_image(img, text, (margin + line_width, v_pos), color, line_width)
                        v_pos += int(bottom_border / 2)
                        rank_pos = str(idx+1)
                        text = "Prediction #rank: " + rank_pos + " confidence: {0:.2f}% ".format(float(prediction["confidence"])*100)
                        img, line_width = self.__draw_text_in_image(img, text, (margin, v_pos), white, 0)
                        color = light_red
                        if status == "MATCH!":
                            color = green
                        text = "Result: " + status + " "
                        img, line_width = self.__draw_text_in_image(img, text, (margin + line_width, v_pos), color, line_width)

                        font = cv2.FONT_HERSHEY_SIMPLEX
                        if ovmax > 0:
                            bbgt = [ int(x) for x in gt_match["bbox"].split() ]
                            cv2.rectangle(img,(bbgt[0],bbgt[1]),(bbgt[2],bbgt[3]),light_blue,2)
                            cv2.rectangle(img_cumulative,(bbgt[0],bbgt[1]),(bbgt[2],bbgt[3]),light_blue,2)
                            cv2.putText(img_cumulative, class_name, (bbgt[0],bbgt[1] - 5), font, 0.6, light_blue, 1, cv2.LINE_AA)
                        bb = [int(i) for i in bb]
                        cv2.rectangle(img,(bb[0],bb[1]),(bb[2],bb[3]),color,2)
                        cv2.rectangle(img_cumulative,(bb[0],bb[1]),(bb[2],bb[3]),color,2)
                        cv2.putText(img_cumulative, class_name, (bb[0],bb[1] - 5), font, 0.6, color, 1, cv2.LINE_AA)
                        cv2.imshow("Animation", img)
                        cv2.waitKey(20)
                        output_img_path = results_files_path + "/images/single_predictions/" + class_name + "_prediction" + str(idx) + ".jpg"
                        cv2.imwrite(output_img_path, img)
                        cv2.imwrite(img_cumulative_path, img_cumulative)

                cumsum = 0
                for idx, val in enumerate(fp):
                    fp[idx] += cumsum
                    cumsum += val
                cumsum = 0
                for idx, val in enumerate(tp):
                    tp[idx] += cumsum
                    cumsum += val
                rec = tp[:]
                for idx, val in enumerate(tp):
                    rec[idx] = float(tp[idx]) / gt_counter_per_class[class_name]
                prec = tp[:]
                for idx, val in enumerate(tp):
                    prec[idx] = float(tp[idx]) / (fp[idx] + tp[idx])

                ap, mrec, mprec = self.__voc_ap(rec, prec)
                sum_AP += ap
                text = "{0:.2f}%".format(ap*100) + " = " + class_name + " AP  "
                
                rounded_prec = [ '%.2f' % elem for elem in prec ]
                rounded_rec = [ '%.2f' % elem for elem in rec ]
                results_file.write(text + "\n Precision: " + str(rounded_prec) + "\n Recall   :" + str(rounded_rec) + "\n\n")
                if not self._args.quiet:
                    print(text)
                ap_dictionary[class_name] = ap

                if draw_plot:
                    plt.plot(rec, prec, '-o')
                    area_under_curve_x = mrec[:-1] + [mrec[-2]] + [mrec[-1]]
                    area_under_curve_y = mprec[:-1] + [0.0] + [mprec[-1]]
                    plt.fill_between(area_under_curve_x, 0, area_under_curve_y, alpha=0.2, edgecolor='r')
                    fig = plt.gcf()
                    fig.canvas.set_window_title('AP ' + class_name)
                    plt.title('class: ' + text)
                    plt.xlabel('Recall')
                    plt.ylabel('Precision')
                    axes = plt.gca()
                    axes.set_xlim([0.0,1.0])
                    axes.set_ylim([0.0,1.05])
                    fig.savefig(results_files_path + "/classes/" + class_name + ".png")
                    plt.cla()

            if show_animation:
                cv2.destroyAllWindows()

            results_file.write("\n# mAP of all classes\n")
            mAP = sum_AP / n_classes
            text = "mAP = {0:.2f}%".format(mAP*100)
            results_file.write(text + "\n")
            print(text)
            return count_true_positives, ap_dictionary, mAP
    
    def __countTotalPredictions(self, predicted_files_list):
        pred_counter_per_class = {}
        for txt_file in predicted_files_list:
            lines_list = self.__file_lines_to_list(txt_file)
            for line in lines_list:
                class_name = line.split()[0]
                if class_name in self._args.ignore:
                    continue
                if class_name in pred_counter_per_class:
                    pred_counter_per_class[class_name] += 1
                else:
                    pred_counter_per_class[class_name] = 1
        pred_classes = list(pred_counter_per_class.keys())
        return pred_classes, pred_counter_per_class


    def __plotTotalNumberOccurenceGroundTruth(self, draw_plot, ground_truth_files_list, n_classes, results_files_path, gt_counter_per_class):
        if draw_plot:
            window_title = "Ground-Truth Info"
            plot_title = "Ground-Truth\n"
            plot_title += "(" + str(len(ground_truth_files_list)) + " files and " + str(n_classes) + " classes)"
            x_label = "Number of objects per class"
            output_path = results_files_path + "/Ground-Truth Info.png"
            to_show = False
            plot_color = 'forestgreen'
            self.__draw_plot_func(
                gt_counter_per_class,
                n_classes,
                window_title,
                plot_title,
                x_label,
                output_path,
                to_show,
                plot_color,
                '',
                )


    def __writeGroundTruthObjects(self, results_files_path, gt_counter_per_class):
        with open(results_files_path + "/results.txt", 'a') as results_file:
            results_file.write("\n# Number of ground-truth objects per class\n")
            for class_name in sorted(gt_counter_per_class):
                results_file.write(class_name + ": " + str(gt_counter_per_class[class_name]) + "\n")


    def __countingTruePositives(self, pred_classes, gt_classes, count_true_positives):
        for class_name in pred_classes:
            if class_name not in gt_classes:
                count_true_positives[class_name] = 0

    
    def __writePredictedObjects(self, results_files_path, pred_classes, pred_counter_per_class, count_true_positives):
        with open(results_files_path + "/results.txt", 'a') as results_file:
            results_file.write("\n# Number of predicted objects per class\n")
            for class_name in sorted(pred_classes):
                n_pred = pred_counter_per_class[class_name]
                text = class_name + ": " + str(n_pred)
                text += " (tp:" + str(count_true_positives[class_name]) + ""
                text += ", fp:" + str(n_pred - count_true_positives[class_name]) + ")\n"
                results_file.write(text)
    
    def __plotTotalNumberOcurrencesPredicted(self, draw_plot, predicted_files_list, pred_counter_per_class, results_files_path, count_true_positives):
        if draw_plot:
            window_title = "Predicted Objects Info"
            plot_title = "Predicted Objects\n"
            plot_title += "(" + str(len(predicted_files_list)) + " files and "
            count_non_zero_values_in_dictionary = sum(int(x) > 0 for x in list(pred_counter_per_class.values()))
            plot_title += str(count_non_zero_values_in_dictionary) + " detected classes)"
            x_label = "Number of objects per class"
            output_path = results_files_path + "/Predicted Objects Info.png"
            to_show = False
            plot_color = 'forestgreen'
            true_p_bar = count_true_positives
            self.__draw_plot_func(
                pred_counter_per_class,
                len(pred_counter_per_class),
                window_title,
                plot_title,
                x_label,
                output_path,
                to_show,
                plot_color,
                true_p_bar
                )

    def __plotmAP(self, draw_plot, results_files_path, ap_dictionary, n_classes, mAP):
        if draw_plot:
            window_title = "mAP"
            plot_title = "mAP = {0:.2f}%".format(mAP*100)
            x_label = "Average Precision"
            output_path = results_files_path + "/mAP.png"
            to_show = False
            plot_color = 'royalblue'
            self.__draw_plot_func(
                ap_dictionary,
                n_classes,
                window_title,
                plot_title,
                x_label,
                output_path,
                to_show,
                plot_color,
                ""
            )


    def __error(self, msg):
        print(msg)
        sys.exit(0)

  
    def __is_float_between_0_and_1(self, value):
        try:
            val = float(value)
            if val > 0.0 and val < 1.0:
                return True
            else:
                return False
        except ValueError:
            return False


    def __voc_ap(self, rec, prec):
       
        rec.insert(0, 0.0)
        rec.append(1.0)
        mrec = rec[:]
        prec.insert(0, 0.0)
        prec.append(0.0)
        mpre = prec[:]
       
        for i in range(len(mpre)-2, -1, -1):
            mpre[i] = max(mpre[i], mpre[i+1])
       
        i_list = []
        for i in range(1, len(mrec)):
            if mrec[i] != mrec[i-1]:
                i_list.append(i)
      
        ap = 0.0
        for i in i_list:
            ap += ((mrec[i]-mrec[i-1])*mpre[i])
        return ap, mrec, mpre


    def __file_lines_to_list(self, path):
        with open(path) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        return content

 
    def __draw_text_in_image(self, img, text, pos, color, line_width):
        font = cv2.FONT_HERSHEY_PLAIN
        fontScale = 1
        lineType = 1
        bottomLeftCornerOfText = pos
        cv2.putText(img, text,
            bottomLeftCornerOfText,
            font,
            fontScale,
            color,
            lineType)
        text_width, _ = cv2.getTextSize(text, font, fontScale, lineType)[0]
        return img, (line_width + text_width)


    def __adjust_axes(self, r, t, fig, axes):
        bb = t.get_window_extent(renderer=r)
        text_width_inches = bb.width / fig.dpi
        current_fig_width = fig.get_figwidth()
        new_fig_width = current_fig_width + text_width_inches
        propotion = new_fig_width / current_fig_width
        x_lim = axes.get_xlim()
        axes.set_xlim([x_lim[0], x_lim[1]*propotion])


    def __draw_plot_func(self, dictionary, n_classes, window_title, plot_title, x_label, output_path, to_show, plot_color, true_p_bar):
        sorted_dic_by_value = sorted(dictionary.items(), key=operator.itemgetter(1))
        sorted_keys, sorted_values = zip(*sorted_dic_by_value)
        if true_p_bar != "":
          
            fp_sorted = []
            tp_sorted = []
            for key in sorted_keys:
                fp_sorted.append(dictionary[key] - true_p_bar[key])
                tp_sorted.append(true_p_bar[key])
            plt.barh(range(n_classes), fp_sorted, align='center', color='crimson', label='False Predictions')
            plt.barh(range(n_classes), tp_sorted, align='center', color='forestgreen', label='True Predictions', left=fp_sorted)
            plt.legend(loc='lower right')
           
            fig = plt.gcf()
            axes = plt.gca()
            r = fig.canvas.get_renderer()
            for i, val in enumerate(sorted_values):
                fp_val = fp_sorted[i]
                tp_val = tp_sorted[i]
                fp_str_val = " " + str(fp_val)
                tp_str_val = fp_str_val + " " + str(tp_val)
                t = plt.text(val, i, tp_str_val, color='forestgreen', va='center', fontweight='bold')
                plt.text(val, i, fp_str_val, color='crimson', va='center', fontweight='bold')
                if i == (len(sorted_values)-1):
                    self.__adjust_axes(r, t, fig, axes)
        else:
            plt.barh(range(n_classes), sorted_values, color=plot_color)
            fig = plt.gcf()
            axes = plt.gca()
            r = fig.canvas.get_renderer()
            for i, val in enumerate(sorted_values):
                str_val = " " + str(val)
                if val < 1.0:
                    str_val = " {0:.2f}".format(val)
                t = plt.text(val, i, str_val, color=plot_color, va='center', fontweight='bold')
                if i == (len(sorted_values)-1):
                    self.__adjust_axes(r, t, fig, axes)
        fig.canvas.set_window_title(window_title)
        tick_font_size = 12
        plt.yticks(range(n_classes), sorted_keys, fontsize=tick_font_size)
        
        init_height = fig.get_figheight()
        dpi = fig.dpi
        height_pt = n_classes * (tick_font_size * 1.4)
        height_in = height_pt / dpi
        top_margin = 0.15
        bottom_margin = 0.05
        figure_height = height_in / (1 - top_margin - bottom_margin)
        if figure_height > init_height:
            fig.set_figheight(figure_height)

        plt.title(plot_title, fontsize=14)
        plt.xlabel(x_label, fontsize='large')
        fig.tight_layout()
        fig.savefig(output_path)
        if to_show:
            plt.show()
        plt.close()


if __name__ == '__main__':
    mAP = mAP()
    mAP.main()