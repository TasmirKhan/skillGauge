import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;

public class DsaPractice {
    public static void main(String[] args) {
        List<Integer> questionIds = new ArrayList<>();
        for (int i = 101; i <= 140; i++) {
            questionIds.add(i);
        }

        Random random = new Random(42);
        Collections.shuffle(questionIds, random);

        Set<Integer> selected = new LinkedHashSet<>();
        for (int id : questionIds) {
            if (selected.size() == 5) {
                break;
            }
            selected.add(id);
        }

        System.out.println("DSA Practice: randomized unique question selections");
        System.out.println("Selected question IDs: " + selected);
    }
}
