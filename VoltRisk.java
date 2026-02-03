import java.util.*;

public class VoltRisk {
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        Random r = new Random();
        int score = 0;
        System.out.println("Reach 50 to win. Roll a 1 and you lose!");

        while (score < 50) {
            System.out.print("Current Score: " + score + " | (1) Roll (2) Quit: ");
            if (s.nextInt() == 2) break;
            
            int roll = r.nextInt(6) + 1;
            System.out.println("You rolled a: " + roll);
            
            if (roll == 1) {
                score = 0;
                System.out.println("VOLT CRASHED! Score reset.");
                break;
            }
            score += roll;
        }
        System.out.println(score >= 50 ? "SYSTEM OVERLOAD: YOU WIN!" : "GAME OVER.");
    }
}